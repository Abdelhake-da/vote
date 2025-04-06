# Script to set up media directories for the ImageVoting project
import os
import sys

# Define the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the media directory paths
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
PHOTOS_DIR = os.path.join(MEDIA_ROOT, 'photos')

def setup_media_directories():
    """Create the necessary media directories if they don't exist"""
    print(f"Setting up media directories in {BASE_DIR}")
    
    # Create the main media directory
    if not os.path.exists(MEDIA_ROOT):
        print(f"Creating media directory: {MEDIA_ROOT}")
        os.makedirs(MEDIA_ROOT)
    else:
        print(f"Media directory already exists: {MEDIA_ROOT}")
    
    # Create the photos directory
    if not os.path.exists(PHOTOS_DIR):
        print(f"Creating photos directory: {PHOTOS_DIR}")
        os.makedirs(PHOTOS_DIR)
    else:
        print(f"Photos directory already exists: {PHOTOS_DIR}")
    
    # Set permissions (if needed)
    try:
        os.chmod(MEDIA_ROOT, 0o755)  # rwxr-xr-x
        os.chmod(PHOTOS_DIR, 0o755)  # rwxr-xr-x
        print("Set directory permissions to 755")
    except Exception as e:
        print(f"Warning: Could not set permissions: {str(e)}")
    
    print("Media directories setup complete!")

if __name__ == "__main__":
    setup_media_directories()
