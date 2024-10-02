import os
import sys
import multiprocessing as mp

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

ASSETS_DIR = os.path.join(base_path, 'assets')
UPLOAD_DIR = os.path.join(ASSETS_DIR, 'uploads')
PYCACHE_DIR = os.path.join(base_path, '__pycache__')
PROCESSED_FRAMES_DIR = os.path.join(ASSETS_DIR, 'processed_frames')
OUTPUT_VIDEO_DIR = os.path.join(base_path, 'video_output')
VIDEO_PREVIEW_FILE = os.path.join(ASSETS_DIR, 'video_preview.png')
AUDIO_FILE = os.path.join(ASSETS_DIR, 'bad_apple_enhanced.mp3')
ICON_FILE = os.path.join(ASSETS_DIR, 'badApple.ico')
IMAGE_FILE = os.path.join(ASSETS_DIR, 'badApple.png')
PIXEL_DATA_DIR = os.path.join(base_path, 'pixel_data')

NUM_PROCESSES = max(2, int(mp.cpu_count() * 0.7))

DEFAULT_INPUT_RESOLUTION = '48p'
DEFAULT_FRAMERATE = '30fps'
DEFAULT_OUTPUT_RESOLUTION = '1080p'

OUTPUT_RESOLUTION_DIMENSIONS = {
    '4K': (2880, 2160),
    '2K': (1920, 1440),
    '1080p': (1440, 1080)
}

FRAME_RATE_OPTIONS = {
    '30fps': 30,
    '60fps': 60
}
