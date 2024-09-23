import os
import sys

# Determine the base path
if getattr(sys, 'frozen', False):
    # Running in a bundled executable
    base_path = sys._MEIPASS
else:
    # Running as a script
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Paths relative to base_path
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

# Default settings for dropdown
DEFAULT_INPUT_RESOLUTION = '72p'
DEFAULT_FRAMERATE = '30fps'
DEFAULT_OUTPUT_RESOLUTION = '4K'

# Mapping for output resolutions to dimensions
OUTPUT_RESOLUTION_DIMENSIONS = {
    '4K': (2880, 2160),
    '2K': (1920, 1440),
    '1080p': (1440, 1080)
}

# Frame rate options
FRAME_RATE_OPTIONS = {
    '30fps': 30,
    '60fps': 60
}
