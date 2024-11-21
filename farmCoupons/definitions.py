# Standard library imports
import platform
from pathlib import Path

# Third-party imports
import pyautogui
from pytesseract import pytesseract

# Constants and configuration
BASE_DIR = Path(__file__).parent  # Base directory of the project
DATABASE_URL = "mongodb://user:password@ip:port"  # MongoDB connection URL

# Configure Tesseract command based on operating system
if platform.system() == 'Linux':
    pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Tesseract command for Linux
else:
    pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'  # Tesseract command for Windows

# Asset directory path
ASSET_DIRECTORY = f'{BASE_DIR}/assets'
PUPPETEER_PROFILE_DIR = f'{BASE_DIR}/puppeteer-profile'
