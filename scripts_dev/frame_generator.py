import cv2 as cv
import os
import numpy as np
import sys

def generate_frames(input_video_path, output_dir):
    # Create the output directory if it doesn't exist
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"Output directory '{output_dir}' created or already exists.")
    except Exception as e:
        print(f"Error creating output directory: {e}")
        return

    # Open the input video
    input_video = cv.VideoCapture(input_video_path)

    if not input_video.isOpened():
        print(f"Error opening video file '{input_video_path}'")
        return

    # Get video properties
    width = int(input_video.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(input_video.get(cv.CAP_PROP_FRAME_HEIGHT))
    fps = input_video.get(cv.CAP_PROP_FPS)
    frame_count = int(input_video.get(cv.CAP_PROP_FRAME_COUNT))

    print(f"Processing video: {input_video_path}")
    print(f"Resolution: {width}x{height}, FPS: {fps}, Total Frames: {frame_count}")

    frame_counter = 0

    while True:
        ret, frame = input_video.read()
        if not ret:
            print("No more frames to read or error reading frame.")
            break

        # Convert frame to grayscale
        gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # Apply binary thresholding
        _, binary_frame = cv.threshold(gray_frame, 128, 255, cv.THRESH_BINARY)

        # Save the frame as an image in the output directory
        output_frame_path = os.path.join(output_dir, f'frame_{frame_counter:04d}.png')
        cv.imwrite(output_frame_path, binary_frame)
        print(f"Saved frame {frame_counter} to '{output_frame_path}'")

        frame_counter += 1

    # Release video capture object
    input_video.release()
    cv.destroyAllWindows()

    print(f"All frames saved to '{output_dir}'. Total frames processed: {frame_counter}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python frame_generator.py <input_video_path> <output_dir>")
        sys.exit(1)
    input_video_path = sys.argv[1]
    output_dir = sys.argv[2]
    generate_frames(input_video_path, output_dir)
