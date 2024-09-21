import cv2 as cv
import ffmpeg
import numpy as np
import os
import shutil
import pickle
import concurrent.futures
import multiprocessing as mp
import config

mp.set_start_method("spawn", force=True)

executor_reference = None

def load_image_as_cv_array(path):
    """
    Loads an image using OpenCV and resizes it to 40x40 pixels.

    Args:
        path (str): Path to the image file.

    Returns:
        np.ndarray: Resized image array.
    """
    return cv.resize(cv.imread(path), (40, 40))

def generate_frame(frame_info):
    """
    Generates individual frames by overlaying user images and saves them as PNG files.

    Args:
        frame_info (tuple): Frame data and pixel values.
    """
    key, value = frame_info
    user_img_array = load_image_as_cv_array(os.path.join(config.UPLOAD_DIR, "40x40_upload.png"))
    gray_user_img_array = load_image_as_cv_array(os.path.join(config.UPLOAD_DIR, "gray_40x40_upload.png"))
    blank_frame_array = np.zeros((2160, 2880, 3), dtype=np.uint8)
    output_dir = config.PROCESSED_FRAMES_DIR

    frame_number = f"frame_{int(key):05d}.png"
    frame_array = blank_frame_array.copy()

    posx, posy = 0, 0
    for pixel in value:
        frame_array[posy:posy + 40, posx:posx + 40] = user_img_array if pixel == 1 else gray_user_img_array
        posx += 40
        if posx >= 2880:
            posx = 0
            posy += 40
        if posy >= 2160:
            break
    cv.imwrite(os.path.join(output_dir, frame_number), frame_array, [cv.IMWRITE_PNG_COMPRESSION, 1])

def generate_frames():
    global executor_reference

    output_dir = config.PROCESSED_FRAMES_DIR
    os.makedirs(output_dir, exist_ok=True)

    pixel_data_path = config.PIXEL_DATA_FILE
    with open(pixel_data_path, "rb") as file:
        pixel_data = pickle.load(file)

    num_processes = max(2, int(mp.cpu_count() * 0.8))
    executor = concurrent.futures.ProcessPoolExecutor(max_workers=num_processes)
    executor_reference = executor

    try:
        pool_inputs = [frame_info for frame_info in pixel_data.items()]
        list(executor.map(generate_frame, pool_inputs))
    finally:
        executor.shutdown(wait=True)
        executor_reference = None

def generate_video(frames_dir, fps, output_video_path, audio_path):
    """
    Combines the generated frames into a video and merges it with the audio.

    Args:
        frames_dir (str): Directory containing frame images.
        fps (int): Frames per second for the video.
        output_video_path (str): Path to the output video file.
        audio_path (str): Path to the audio file to be merged with the video.
    """

    try:
        output_dir = os.path.dirname(output_video_path)
        os.makedirs(output_dir, exist_ok=True)
        input_video = ffmpeg.input(os.path.join(frames_dir, "frame_%05d.png"), framerate=fps)
        input_audio = ffmpeg.input(audio_path)

        ffmpeg.concat(input_video, input_audio, v=1, a=1).output(
            output_video_path, vcodec="libx264", pix_fmt="yuv420p", acodec="aac", strict="experimental", format="mp4"
        ).run(overwrite_output=True)
    except Exception as e:
        raise e
    finally:
        cleanup()

def cleanup():
    """
    Cleans up unused directories after video generation.
    """
    try:
        shutil.rmtree(config.UPLOAD_DIR)
    except Exception:
        pass

    try:
        shutil.rmtree(config.PROCESSED_FRAMES_DIR)
    except Exception:
        pass

    try:
        shutil.rmtree(config.PYCACHE_DIR)
    except Exception:
        pass
