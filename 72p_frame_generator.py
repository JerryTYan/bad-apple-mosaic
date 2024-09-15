#ffmpeg -i bad_apple@2160p60fps.mp4 -vf "scale=72:54" bad_apple@72p60fps.mp4

import cv2 as cv
import os
import numpy as np

# Create the output directory if it doesn't exist
output_dir = 'assets/72p_frames'
os.makedirs(output_dir, exist_ok=True)

# Open the input video
input_video = cv.VideoCapture('bad_apple@72p60fps.mp4')

# Get video properties
width = int(input_video.get(cv.CAP_PROP_FRAME_WIDTH))
height = int(input_video.get(cv.CAP_PROP_FRAME_HEIGHT))
fps = int(input_video.get(cv.CAP_PROP_FPS))

frame_counter = 0

while input_video.isOpened():
    ret, frame = input_video.read()
    if not ret:
        break

    # Convert frame to grayscale
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # Apply binary thresholding
    _, binary_frame = cv.threshold(gray_frame, 128, 255, cv.THRESH_BINARY)

    # Force all pixel values to either 0 or 255
    binary_frame = np.where(binary_frame > 128, 255, 0).astype(np.uint8)

    # Save the frame as an image in the output directory
    output_frame_path = os.path.join(output_dir, f'frame_{frame_counter:04d}.png')
    cv.imwrite(output_frame_path, binary_frame)

    frame_counter += 1

# Release video capture object
input_video.release()
cv.destroyAllWindows()

print(f"All frames saved to '{output_dir}'.")
