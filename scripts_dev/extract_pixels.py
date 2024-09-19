from collections import OrderedDict
from bitarray import bitarray
import pickle
import os
import re
import cv2 as cv

# Function to extract the frame number from file name using RegEx
def extract_frame_number(file_name):
    frame_number = re.search(r"(\d+)", file_name)
    return int(frame_number.group()) if frame_number else -1 # Return frame_number if it is not None

# Extract binary bits from frame to insert into bit array
def bit_extraction(frame):
    return [1 if pixel == 255 else 0 for row in frame for pixel in row]

# Input directory with 72p frames
input_dir = "assets/frames@72p30fps"

# Store pixel data in an ordered dictionary with frame numbers as keys
pixel_data = OrderedDict()

# Extract list of sorted frame files
raw_frame_files = sorted(os.listdir(input_dir), key=extract_frame_number)

# Inserts frame number as key and pixel data bit array as value into ordered dict
for frame_file in raw_frame_files:
    frame_path = os.path.join(input_dir, frame_file)
    frame = cv.imread(frame_path, cv.IMREAD_GRAYSCALE)
    if frame is None:
        print(f"Error reading frame: {frame_path}")
        continue # Skip frames that fail to load
    frame_data = bitarray(bit_extraction(frame)) # 1 for white, 0 for black
    frame_number = int(frame_file.split('_')[1].split('.')[0])
    pixel_data[frame_number] = frame_data
    
# Serialize data using pickle
with open('pixel_data@72p30fps.pkl', 'wb') as file:
    pickle.dump(pixel_data, file)
