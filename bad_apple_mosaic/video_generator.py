import cv2 as cv
import ffmpeg
import numpy as np
import os
import sys
import shutil
import pickle
import concurrent.futures
import multiprocessing as mp
import subprocess
import config

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

    # After generating frames, save frame 250 as "video_preview.png"
    frame_number = 250
    frame_filename = f"frame_{frame_number:05d}.png"
    frame_path = os.path.join(output_dir, frame_filename)
    if os.path.exists(frame_path):
        shutil.copyfile(frame_path, config.VIDEO_PREVIEW_FILE)
    else:
        print(f"Frame {frame_number} not found at {frame_path}. Cannot create video preview.")

def get_ffmpeg_executable():
    """
    Returns the path to the ffmpeg executable.
    If running as a packaged executable, it assumes ffmpeg.exe is in the same directory.
    If running as a script, it assumes ffmpeg.exe is in the parent directory of the script.
    """
    if getattr(sys, 'frozen', False):
        # Running in a bundle (PyInstaller)
        base_path = sys._MEIPASS
        ffmpeg_exe = os.path.join(base_path, 'ffmpeg.exe')
    else:
        # Running in a normal Python environment
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        ffmpeg_exe = os.path.join(base_path, 'ffmpeg.exe')

    ffmpeg_exe = os.path.abspath(ffmpeg_exe)

    return ffmpeg_exe

def generate_video(frames_dir, fps, output_video_path, audio_path):
    try:
        output_dir = os.path.dirname(output_video_path)
        os.makedirs(output_dir, exist_ok=True)

        ffmpeg_exe = get_ffmpeg_executable()

        # Build the FFmpeg command
        input_pattern = os.path.join(frames_dir, "frame_%05d.png")
        ffmpeg_cmd = [
            ffmpeg_exe,
            '-y',  # Overwrite output files without asking
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

        # Set creationflags to suppress console window (Windows only)
        creationflags = 0
        if os.name == 'nt':
            creationflags = subprocess.CREATE_NO_WINDOW

        # Run the FFmpeg command
        process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=creationflags
        )

        # Wait for the process to complete
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise Exception(f"FFmpeg error: {stderr.decode()}")

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

if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    