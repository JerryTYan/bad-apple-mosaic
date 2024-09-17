from PIL import Image
import pickle
import os
import time
import multiprocessing as mp
from collections import OrderedDict
from bitarray import bitarray

output_dir = "assets/processed_frames"
os.makedirs(output_dir, exist_ok=True)

# Load user images
user_img = Image.open("assets/uploads/40x40_upload.png").convert('RGBA')
gray_user_img = Image.open("assets/uploads/gray_40x40_upload.png").convert('RGBA')

# Load pixel data (bitarray for each frame)
with open('pixel_data.pkl', 'rb') as file:
    pixel_data = pickle.load(file)

# Constants for frame size and tile size
FRAME_WIDTH = 2880
FRAME_HEIGHT = 2160
TILE_SIZE = 40

# Function to generate a single frame
def generate_frame(frame_info):
    key, value = frame_info
    
    # Open a blank 4K frame for modification
    blank_frame = Image.open("assets/4k_blank_frame.png").convert('RGBA')
    frame_number = f"frame_{int(key):05d}.png"
    
    # Initialize new position values for each frame
    posx, posy = 0, 0
    
    # Edit blank frame
    for pixel in value:
        position = (posx, posy)

        # Place the user image on white pixels
        if pixel == 1:  # white
            blank_frame.paste(user_img, position, user_img)
            
        else: # black
            blank_frame.paste(gray_user_img, position, gray_user_img)
        
        # Move to the next tile position
        posx += TILE_SIZE

        # End of row: reset x and move down to the next row
        if posx >= FRAME_WIDTH:
            posx = 0
            posy += TILE_SIZE
        
        # End of frame: stop if the bottom of the frame is reached
        if posy >= FRAME_HEIGHT:
            break
    
    # Save the processed frame
    blank_frame.save(os.path.join(output_dir, frame_number))

# Start multi-processing
if __name__ == "__main__":
    start_time = time.time()
    
    # Create a pool of workers (number of processes = number of CPU cores)
    with mp.Pool(mp.cpu_count()) as pool:
        # Map the frame generation function to each frame in the pixel data
        pool.map(generate_frame, pixel_data.items())
    
    end_time = time.time()
    
    total_time = end_time - start_time
    print(f"Frame generation complete in {total_time:.2f} seconds.")
