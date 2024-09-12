#ffmpeg -i bad_apple@2160p60fps.mp4 -vf "scale=72:54" bad_apple@72p60fps.mp4

import cv2
import os
import numpy as np

# Create the output directory if it doesn't exist
output_dir = 'assets/72p_frames'
os.makedirs(output_dir, exist_ok=True)

# Open the input video
input_video = cv2.VideoCapture('bad_apple@72p60fps.mp4')

# Get video properties
width = int(input_video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(input_video.get(cv2.CAP_PROP_FPS))

frame_counter = 0

while input_video.isOpened():
    ret, frame = input_video.read()
    if not ret:
        break

    # Convert frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply binary thresholding
    _, binary_frame = cv2.threshold(gray_frame, 128, 255, cv2.THRESH_BINARY)

    # Force all pixel values to either 0 or 255
    binary_frame = np.where(binary_frame > 128, 255, 0).astype(np.uint8)

    # Save the frame as an image in the output directory
    output_frame_path = os.path.join(output_dir, f'frame_{frame_counter:04d}.png')
    cv2.imwrite(output_frame_path, binary_frame)

    frame_counter += 1

# Release video capture object
input_video.release()
cv2.destroyAllWindows()

print(f"All frames saved to '{output_dir}'.")
