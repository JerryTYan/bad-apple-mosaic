import cv2 as cv
import ffmpeg
import numpy as np
import os
import time
import shutil
import pickle
import multiprocessing as mp
import config

mp.set_start_method('spawn', force=True)

def load_image_as_cv_array(path):
    """
    Loads an image using OpenCV and resizes it to 40x40 pixels.

    Args:
        path (str): Path to the image file.

    Returns:
        np.ndarray: Resized image array.
    """
    return cv.resize(cv.imread(path), (40, 40))

def generate_frame(frame_info, user_img_array, gray_user_img_array, blank_frame_array, output_dir):
    """
    Generates individual frames by overlaying user images and saves them as PNG files.

    Args:
        frame_info (tuple): Frame data and pixel values.
        user_img_array (np.ndarray): Color image array of the user's image.
        gray_user_img_array (np.ndarray): Grayscale version of the user's image.
        blank_frame_array (np.ndarray): Blank frame template.
        output_dir (str): Directory where the generated frames will be saved.
    """
    key, value = frame_info
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
    """
    Generates all frames in parallel using multiple CPU cores.
    """
    output_dir = config.PROCESSED_FRAMES_DIR
    try:
        os.makedirs(output_dir, exist_ok=True)
        
    except OSError as e:
        messagebox.showerror("Directory Error", f"Could not create PROCESSED_FRAMES_DIR directory: {e}")
        return

    try:
        user_img_path = os.path.join(config.UPLOAD_DIR, '40x40_upload.png')
        gray_user_img_path = os.path.join(config.UPLOAD_DIR, 'gray_40x40_upload.png')
        user_img_array = load_image_as_cv_array(user_img_path)
        gray_user_img_array = load_image_as_cv_array(gray_user_img_path)
        blank_frame_array = np.zeros((2160, 2880, 3), dtype=np.uint8)

        pixel_data_path = config.PIXEL_DATA_FILE
        with open(pixel_data_path, 'rb') as file:
            pixel_data = pickle.load(file)
            
    except FileNotFoundError as e:
        messagebox.showerror("File Error", f"Missing necessary files: {e}")
        return
    except Exception as e:
        messagebox.showerror("Frame Generation Error", f"An unexpected error occured while generating frames: {e}")
        return

    try:
        ctx = mp.get_context('spawn')
        num_processes = max(2, int(mp.cpu_count() * 0.8))
        pool_inputs = [
            (frame_info, user_img_array, gray_user_img_array, blank_frame_array, output_dir)
            for frame_info in pixel_data.items()
        ]
        with ctx.Pool(num_processes) as pool:
            pool.starmap(generate_frame, pool_inputs)
            
    except Exception as e:
        messagebox.showerror("Multiprocessing Error", f"An unexpected error occured in parallel frame generation: {e}")
        return

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
        input_video = ffmpeg.input(os.path.join(frames_dir, 'frame_%05d.png'), framerate=fps)
        input_audio = ffmpeg.input(audio_path)

        ffmpeg.concat(input_video, input_audio, v=1, a=1).output(
            output_video_path, vcodec='libx264', pix_fmt='yuv420p', acodec='aac', strict='experimental'
        ).run()

    except FileNotFoundError as e:
        messagebox.showerror("File Error", f"Missing audio or frame files: {e}")
        return
    except ffmpeg.Error as e:
        messagebox.showerror("FFmpeg Error", f"Error processing video with FFmpeg: {e}")
        return
    except Exception as e:
        messagebox.showerror("Video Generation Error", f"An unexpected error occurred while generating the video: {e}")
        return
    
    finally:
        cleanup()

def cleanup():
    """
    Cleans up unused directories after video generation.
    """
    try:
        shutil.rmtree(config.UPLOAD_DIR)
    except FileNotFoundError:
        pass
    except PermissionError as e:
        messagebox.showerror("Permission Error", f"Could not remove upload directory: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred while cleaning upload directory: {e}")

    try:
        shutil.rmtree(config.PROCESSED_FRAMES_DIR)
    except FileNotFoundError:
        pass
    except PermissionError as e:
        messagebox.showerror("Permission Error", f"Could not remove processed frames directory: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred while cleaning processed frames directory: {e}")

    try:
        shutil.rmtree(config.PYCACHE_DIR)
    except FileNotFoundError:
        pass
    except PermissionError as e:
        messagebox.showerror("Permission Error", f"Could not remove pycache directory: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred while cleaning pycache directory: {e}")
