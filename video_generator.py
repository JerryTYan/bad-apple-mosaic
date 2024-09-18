import cv2 as cv
import ffmpeg
import numpy as np
import os
import time
import pickle
import multiprocessing as mp

output_dir = "assets/processed_frames"
os.makedirs(output_dir, exist_ok=True)

# Load images as NumPy arrays using OpenCV
def load_image_as_cv_array(path):
    return cv.resize(cv.imread(path), (40, 40))

# Load pixel data
with open('pixel_data@72p30fps.pkl', 'rb') as file:
    pixel_data = pickle.load(file)

# Constants
FRAME_WIDTH = 2880
FRAME_HEIGHT = 2160
TILE_SIZE = 40

# Function to generate frames using OpenCV
def generate_frame(frame_info, user_img_array, gray_user_img_array, blank_frame_array):
    key, value = frame_info
    frame_number = f"frame_{int(key):05d}.png"  # Use .png extension
    
    # Copy the blank frame
    frame_array = blank_frame_array.copy()

    # Initialize new position values
    posx, posy = 0, 0
    
    for pixel in value:
        # If white, paste the user image; if black, paste the gray image
        if pixel == 1:
            frame_array[posy:posy+TILE_SIZE, posx:posx+TILE_SIZE] = user_img_array
        else:
            frame_array[posy:posy+TILE_SIZE, posx:posx+TILE_SIZE] = gray_user_img_array

        # Move to the next tile position
        posx += TILE_SIZE
        if posx >= FRAME_WIDTH:
            posx = 0
            posy += TILE_SIZE
        if posy >= FRAME_HEIGHT:
            break
    
    # Save the frame as PNG using OpenCV
    cv.imwrite(os.path.join(output_dir, frame_number), frame_array, [cv.IMWRITE_PNG_COMPRESSION, 1])

# Generate frames in parallel
def generate_frames():
    user_img_array = load_image_as_cv_array("assets/uploads/40x40_upload.png")
    gray_user_img_array = load_image_as_cv_array("assets/uploads/gray_40x40_upload.png")
    
    # Create a blank frame (3 channels for RGB)
    blank_frame_array = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)

    # Parallel frame generation
    with mp.Pool(max(2, mp.cpu_count() - 2)) as pool:
        pool.starmap(generate_frame, [(frame_info, user_img_array, gray_user_img_array, blank_frame_array) for frame_info in pixel_data.items()])

# Generate video and merge with audio in one step
def generate_video(frames_dir, fps, output_video_path, audio_path):
    input_video = ffmpeg.input(f'{frames_dir}/frame_%05d.png', framerate=fps)
    input_audio = ffmpeg.input(audio_path)

    # Concatenate the video and audio streams
    (
        ffmpeg
        .concat(input_video, input_audio, v=1, a=1)  # Concatenate video and audio
        .output(output_video_path,
                vcodec='libx264',
                pix_fmt='yuv420p',
                acodec='aac',
                strict='experimental',
                shortest=None)
        .run()
    )

if __name__ == "__main__":
    start_time = time.time()
    
    # Generate frames
    print("Generating frames...")
    generate_frames()
    
    # Generate video with audio
    print("Generating video with audio...")
    generate_video('assets/processed_frames', 30, 'good_apple.mp4', 'assets/bad_apple_enhanced.mp3')

    end_time = time.time()
    print(f"Process complete in {end_time - start_time:.2f} seconds.")
