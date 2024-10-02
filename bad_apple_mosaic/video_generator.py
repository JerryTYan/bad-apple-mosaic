import cv2 as cv
import ffmpeg
import numpy as np
import os
import sys
import shutil
import pickle
import concurrent.futures
import multiprocessing as mp
import config
import subprocess

executor_reference = None

def load_image_as_cv_array(path, size):
    """
    Loads an image from the specified path and resizes it to the given size.

    Args:
        path (str): Path to the image file.
        size (tuple): Desired size (width, height) for the image.

    Returns:
        numpy.ndarray: The loaded and resized image as a NumPy array.
    """
    return cv.resize(cv.imread(path), size)

def generate_frame(args):
    """
    Generates a single frame by placing user images according to the pixel data.

    Args:
        args (tuple): A tuple containing:
            - frame_info (tuple): A key-value pair where key is frame number and value is bitarray of pixel data.
            - tile_size (tuple): Size (width, height) of each tile.
            - frame_dimensions (tuple): Dimensions (width, height) of the frame.
            - user_img_array (numpy.ndarray): User image array.
            - gray_user_img_array (numpy.ndarray): Grayscale user image array.
    """
    frame_info, tile_size, frame_dimensions, user_img_array, gray_user_img_array = args
    key, value = frame_info

    output_dir = config.PROCESSED_FRAMES_DIR

    frame_number = f"frame_{int(key):05d}.png"
    frame_array = np.zeros((frame_dimensions[1], frame_dimensions[0], 3), dtype=np.uint8)

    tile_width, tile_height = tile_size
    num_columns = frame_dimensions[0] // tile_width

    posx, posy = 0, 0
    idx = 0
    num_pixels = len(value)

    for row in range(frame_dimensions[1] // tile_height):
        for col in range(num_columns):
            if idx >= num_pixels:
                break
            pixel = value[idx]
            if pixel == 1:
                frame_array[posy:posy + tile_height, posx:posx + tile_width] = user_img_array
            else:
                frame_array[posy:posy + tile_height, posx:posx + tile_width] = gray_user_img_array
            posx += tile_width
            idx += 1
        posx = 0
        posy += tile_height
        if idx >= num_pixels:
            break

    cv.imwrite(os.path.join(output_dir, frame_number), frame_array, [cv.IMWRITE_PNG_COMPRESSION, 1])

def generate_frames(pixel_data_path, output_resolution):
    """
    Generates all frames for the video by processing pixel data and user images.

    Args:
        pixel_data_path (str): Path to the pixel data pickle file.
        output_resolution (tuple): Desired output resolution (width, height) for the frames.
    """
    global executor_reference

    output_dir = config.PROCESSED_FRAMES_DIR
    os.makedirs(output_dir, exist_ok=True)

    with open(pixel_data_path, "rb") as file:
        data = pickle.load(file)
        pixel_data = data['pixel_data']
        frame_dimensions = data['frame_dimensions']

    num_columns = frame_dimensions[0]
    num_rows = frame_dimensions[1]

    tile_width = output_resolution[0] // num_columns
    tile_height = output_resolution[1] // num_rows
    tile_size = (tile_width, tile_height)
    min_tile_size = 20  # Minimum acceptable tile size in pixels

    if tile_width < min_tile_size or tile_height < min_tile_size:
        raise Exception("The calculated tile size is too small. Please select a higher output resolution or lower input resolution.")
    
    adjusted_frame_dimensions = (tile_width * num_columns, tile_height * num_rows)

    if adjusted_frame_dimensions != output_resolution:
        print(f"Adjusted output resolution from {output_resolution} to {adjusted_frame_dimensions} to fit tiles exactly.")
        output_resolution = adjusted_frame_dimensions

    user_img_array = load_image_as_cv_array(os.path.join(config.UPLOAD_DIR, "upload.png"), tile_size)
    gray_user_img_array = load_image_as_cv_array(os.path.join(config.UPLOAD_DIR, "gray_upload.png"), tile_size)

    num_processes = max(2, int(mp.cpu_count() * 0.8))
    executor = concurrent.futures.ProcessPoolExecutor(max_workers=num_processes)
    executor_reference = executor

    try:
        pool_inputs = [
            (frame_info, tile_size, adjusted_frame_dimensions, user_img_array, gray_user_img_array)
            for frame_info in pixel_data.items()
        ]
        list(executor.map(generate_frame, pool_inputs))
    finally:
        executor.shutdown(wait=True)
        executor_reference = None

    frame_number = 250
    frame_filename = f"frame_{frame_number:05d}.png"
    frame_path = os.path.join(output_dir, frame_filename)
    if os.path.exists(frame_path):
        shutil.copyfile(frame_path, config.VIDEO_PREVIEW_FILE)
    else:
        print(f"Frame {frame_number} not found at {frame_path}. Cannot create video preview.")

def get_ffmpeg_executable():
    """
    Retrieves the path to the ffmpeg executable, adjusting for whether the script is frozen (compiled) or not.

    Returns:
        str: Absolute path to the ffmpeg executable.
    """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        ffmpeg_exe = os.path.join(base_path, 'ffmpeg.exe')
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        ffmpeg_exe = os.path.join(base_path, 'ffmpeg.exe')
    ffmpeg_exe = os.path.abspath(ffmpeg_exe)
    return ffmpeg_exe

def generate_video(frames_dir, fps, output_video_path, audio_path):
    """
    Generates the final video by combining frames and audio using ffmpeg.

    Args:
        frames_dir (str): Directory containing the generated frames.
        fps (int): Frames per second for the output video.
        output_video_path (str): Path to save the output video file.
        audio_path (str): Path to the audio file to be added to the video.
    """
    try:
        output_dir = os.path.dirname(output_video_path)
        os.makedirs(output_dir, exist_ok=True)

        ffmpeg_exe = get_ffmpeg_executable()

        input_pattern = os.path.join(frames_dir, "frame_%05d.png")
        ffmpeg_cmd = [
            ffmpeg_exe,
            '-y',
            '-framerate', str(fps),
            '-i', input_pattern,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac',
            '-strict', 'experimental',
            '-shortest',
            output_video_path
        ]

        creationflags = 0
        if os.name == 'nt':
            creationflags = subprocess.CREATE_NO_WINDOW

        process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=creationflags
        )

        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise Exception(f"FFmpeg error: {stderr.decode()}")

    except Exception as e:
        raise e
    finally:
        cleanup()

def cleanup():
    """
    Cleans up temporary directories and files used during the video generation process.
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

if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
