import os
import sys

# Determine the base path
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Paths relative to base_path
ASSETS_DIR = os.path.join(base_path, 'assets')
UPLOAD_DIR = os.path.join(ASSETS_DIR, 'uploads')
PYCACHE_DIR = os.path.join(base_path, '__pycache__')
PROCESSED_FRAMES_DIR = os.path.join(ASSETS_DIR, 'processed_frames')
VIDEO_PREVIEW_FILE = os.path.join(ASSETS_DIR, 'video_preview.png')
OUTPUT_VIDEO = os.path.join(base_path, 'video_output', 'good_apple.mp4')
AUDIO_FILE = os.path.join(ASSETS_DIR, 'bad_apple_enhanced.mp3')
ICON_FILE = os.path.join(ASSETS_DIR, 'badApple.ico')
IMAGE_FILE = os.path.join(ASSETS_DIR, 'badApple.png')
PIXEL_DATA_FILE = os.path.join(base_path, 'pixel_data', 'pixel_data@72p30fps.pkl')
FRAME_RATE = 30
