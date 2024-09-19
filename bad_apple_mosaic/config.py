import os

# Directory of current script (config.py)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Paths relative to script_dir
ASSETS_DIR = os.path.abspath(os.path.join(script_dir, '..', 'assets'))
UPLOAD_DIR = os.path.join(ASSETS_DIR, 'uploads')
PYCACHE_DIR = os.path.join(script_dir, '__pycache__')
PROCESSED_FRAMES_DIR = os.path.join(ASSETS_DIR, 'processed_frames')
OUTPUT_VIDEO = os.path.abspath(os.path.join(script_dir, '..', 'good_apple.mp4'))
AUDIO_FILE = os.path.join(ASSETS_DIR, 'bad_apple_enhanced.mp3')
ICON_FILE = os.path.join(ASSETS_DIR, 'badApple.ico')
IMAGE_FILE = os.path.join(ASSETS_DIR, 'badApple.png')
PIXEL_DATA_DIR = os.path.abspath(os.path.join(script_dir, '..', 'pixel_data'))
PIXEL_DATA_FILE = os.path.join(PIXEL_DATA_DIR, 'pixel_data@72p30fps.pkl')
FRAME_RATE = 30
