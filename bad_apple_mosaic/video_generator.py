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

def load_image_as_cv_array(path, size):
    """
    Loads an image using OpenCV and resizes it to the specified size.

    Args:
        path (str): Path to the image file.
        size (tuple): Desired size (width, height).

    Returns:
        np.ndarray: Resized image array.
    """
    return cv.resize(cv.imread(path), size)

def generate_frame(args):
    """
    Generates individual frames by overlaying user images and saves them as PNG files.

    Args:
        args (tuple): Contains frame_info, tile_size, frame_dimensions, user_img_array, gray_user_img_array
    """
    frame_info, tile_size, frame_dimensions, user_img_array, gray_user_img_array = args
    key, value = frame_info

    output_dir = config.PROCESSED_FRAMES_DIR

    frame_number = f"frame_{int(key):05d}.png"
    frame_array = np.zeros((frame_dimensions[1], frame_dimensions[0], 3), dtype=np.uint8)

    posx, posy = 0, 0
    for pixel in value:
        if pixel == 1:
            frame_array[posy:posy + tile_size[1], posx:posx + tile_size[0]] = user_img_array
        else:
            frame_array[posy:posy + tile_size[1], posx:posx + tile_size[0]] = gray_user_img_array
        posx += tile_size[0]
        if posx >= frame_dimensions[0]:
            posx = 0
            posy += tile_size[1]
        if posy >= frame_dimensions[1]:
            break
    cv.imwrite(os.path.join(output_dir, frame_number), frame_array, [cv.IMWRITE_PNG_COMPRESSION, 1])

def generate_frames(pixel_data_path, output_resolution):
    """
    Generates frames using the pixel data and user images.

    Args:
        pixel_data_path (str): Path to the pixel data .pkl file.
        output_resolution (tuple): Output resolution (width, height).
    """
    global executor_reference

    output_dir = config.PROCESSED_FRAMES_DIR
    os.makedirs(output_dir, exist_ok=True)

    with open(pixel_data_path, "rb") as file:
        pixel_data = pickle.load(file)

    # Determine the number of columns and rows from the pixel data
    sample_frame = next(iter(pixel_data.values()))
    num_tiles = len(sample_frame)

    # Assuming the pixel data represents a grid of tiles
    # Calculate the number of columns and rows
    num_columns = int(output_resolution[0] / 40)  # Original tile size for 72p
    num_rows = int(output_resolution[1] / 40)

    # Adjust columns and rows based on the actual number of tiles
    total_tiles = num_columns * num_rows

    if total_tiles != num_tiles:
        # Recalculate the number of columns and rows
        num_rows = int(num_tiles ** 0.5)
        num_columns = num_rows  # Assuming a square grid for simplicity

        # Recalculate tile sizes
        tile_width = output_resolution[0] // num_columns
        tile_height = output_resolution[1] // num_rows
    else:
        # Use the original tile size
        tile_width = 40
        tile_height = 40

    tile_size = (tile_width, tile_height)
    frame_dimensions = (tile_width * num_columns, tile_height * num_rows)

    # Resize user images to the calculated tile size
    user_img_array = load_image_as_cv_array(os.path.join(config.UPLOAD_DIR, "40x40_upload.png"), tile_size)
    gray_user_img_array = load_image_as_cv_array(os.path.join(config.UPLOAD_DIR, "gray_40x40_upload.png"), tile_size)

    num_processes = max(2, int(mp.cpu_count() * 0.8))
    executor = concurrent.futures.ProcessPoolExecutor(max_workers=num_processes)
    executor_reference = executor

    try:
        pool_inputs = [
            (frame_info, tile_size, frame_dimensions, user_img_array, gray_user_img_array)
            for frame_info in pixel_data.items()
        ]
        list(executor.map(generate_frame, pool_inputs))
    finally:
        executor.shutdown(wait=True)
        executor_reference = None

    # Save frame 250 as "video_preview.png"
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
    