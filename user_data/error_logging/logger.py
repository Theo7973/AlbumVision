import logging 
import os

os.makedirs('logs', exist_ok=True)

logger = logging.getLogger("AlbumVisionLogger")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("logs/error.log")
file_handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(file_handler)