import os
import cv2 as cv
import numpy as np

# Directory to save the blank 4K frames
output_dir = 'assets/4k_blank_frames'
os.makedirs(output_dir, exist_ok=True)

# Frame size for 4K resolution (2880 x 2160)
width, height = 2880, 2160

# Number of frames to generate (up to frame_13139)
num_frames = 13140  # Frame numbering starts from 0, so we need 13140 frames

# Create a blank (black) frame
blank_frame = np.zeros((height, width), dtype=np.uint8)

# Generate and save blank 4K frames
for frame_number in range(num_frames):
    # Create the output filename, zero-padded (e.g., frame_00001.png)
    output_filename = f"frame_{frame_number:05d}.png"
    output_path = os.path.join(output_dir, output_filename)
    
    # Save the blank 4K frame as a PNG file
    cv.imwrite(output_path, blank_frame)

print(f"Generated {num_frames} blank 4K frames in {output_dir}.")
