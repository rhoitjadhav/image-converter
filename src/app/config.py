# Packages
import os

ALLOWED_EXTENSIONS = ["png", "jpeg", "jpg", "pdf"]
STATIC_FILES_DIR = os.getenv("STATIC_FILES_DIR", "scratch")
CONVERTED_IMAGE_RESOLUTION = os.getenv("CONVERTED_IMAGE_RESOLUTION", "3500x3500")
