from collections import OrderedDict
from bitarray import bitarray
import pickle
import os
import re
import cv2 as cv
import sys

def extract_frame_number(file_name):
    """
    Extracts the frame number from a file name using regular expressions.

    Args:
        file_name (str): The name of the frame file.

    Returns:
        int: The extracted frame number, or -1 if not found.
    """
    frame_number = re.search(r"(\d+)", file_name)
    return int(frame_number.group()) if frame_number else -1

def bit_extraction(frame):
    """
    Converts a grayscale image frame into a bit array, where 1 represents a white pixel and 0 represents a black pixel.

    Args:
        frame (numpy.ndarray): The grayscale image frame.

    Returns:
        list: A list of bits representing the pixel data.
    """
    return [1 if pixel == 255 else 0 for row in frame for pixel in row]

def extract_pixels(frames_dir, output_pkl_file):
    """
    Extracts pixel data from image frames in a directory and saves it as a pickle file.

    Args:
        frames_dir (str): Directory containing the image frames.
        output_pkl_file (str): Path to the output pickle file where pixel data will be saved.
    """
    pixel_data = OrderedDict()
    raw_frame_files = sorted(os.listdir(frames_dir), key=extract_frame_number)
    frame_dimensions = None

    for frame_file in raw_frame_files:
        frame_path = os.path.join(frames_dir, frame_file)
        frame = cv.imread(frame_path, cv.IMREAD_GRAYSCALE)
        if frame is None:
            print(f"Error reading frame: {frame_path}")
            continue
        if frame_dimensions is None:
            frame_height, frame_width = frame.shape
            frame_dimensions = (frame_width, frame_height)
        frame_data = bitarray(bit_extraction(frame))
        frame_number = int(frame_file.split('_')[1].split('.')[0])
        pixel_data[frame_number] = frame_data

    data_to_save = {
        'pixel_data': pixel_data,
        'frame_dimensions': frame_dimensions
    }

    with open(output_pkl_file, 'wb') as file:
        pickle.dump(data_to_save, file)

    print(f"Pixel data saved to '{output_pkl_file}' with frame dimensions {frame_dimensions}.")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python extract_pixels.py <frames_dir> <output_pkl_file>")
        sys.exit(1)
    frames_dir = sys.argv[1]
    output_pkl_file = sys.argv[2]
    extract_pixels(frames_dir, output_pkl_file)
