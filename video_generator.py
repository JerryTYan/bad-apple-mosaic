import cv2 as cv
from PIL import Image
import pickle
import os
from collections import OrderedDict
from bitarray import bitarray

output_dir = "assets/processed_frames"
os.makedirs(output_dir, exist_ok=True)

user_img = Image.open("assets/uploads/40x40_upload.png").convert('RGBA')
gray_user_img = Image.open("assets/uploads/gray_40x40_upload.png").convert('RGBA')

with open('pixel_data.pkl', 'rb') as file:
    pixel_data = pickle.load(file)

# For every frame
for key, value in pixel_data.items():
    # Open blank frame
    blank_frame = Image.open("assets/4k_blank_frame.png").convert('RGBA')
    frame_number = f"frame_{int(key):05d}.png"
    # Edit blank frame
    pixel_bit_array = value
    for pixel in pixel_bit_array:
        
    # Save blank frame
    