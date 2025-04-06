# Script to check and fix media directory setup
import os
import sys
from django.conf import settings
import django

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ImageVoting.settings')
django.setup()

# Now we can import Django settings
from django.conf import settings

def check_media_setup():
    """Check and fix media directory setup"""
    # Get media paths from Django settings
    media_root = settings.MEDIA_ROOT
    media_url = settings.MEDIA_URL
    
    print("=== Media Directory Setup Check ===")
    print(f"MEDIA_ROOT: {media_root}")
    print(f"MEDIA_URL: {media_url}")
    
    # Check if media root exists
    if not os.path.exists(media_root):
        print(f"Creating media root directory: {media_root}")
        try:
            os.makedirs(media_root)
            print("✓ Media root directory created successfully")
        except Exception as e:
            print(f"✗ Error creating media root directory: {str(e)}")
            return False
    else:
        print("✓ Media root directory exists")
    
    # Check photos directory
    photos_dir = os.path.join(media_root, 'photos')
    if not os.path.exists(photos_dir):
        print(f"Creating photos directory: {photos_dir}")
        try:
            os.makedirs(photos_dir)
            print("✓ Photos directory created successfully")
        except Exception as e:
            print(f"✗ Error creating photos directory: {str(e)}")
            return False
    else:
        print("✓ Photos directory exists")
    
    # Check permissions
    try:
        # Try to create a test file
        test_file_path = os.path.join(media_root, 'test_write.txt')
        with open(test_file_path, 'w') as f:
            f.write('Test write access')
        
        # If we get here, we have write access
        print("✓ Write access to media directory confirmed")
        
        # Clean up test file
        os.remove(test_file_path)
    except Exception as e:
        print(f"✗ Write access test failed: {str(e)}")
        print("This may indicate a permissions issue with the media directory.")
        return False
    
    print("\n=== Media Directory Setup Complete ===")
    print("The media directories are properly set up and have the correct permissions.")
    print("If you're still having issues with image uploads, check the following:")
    print("1. Make sure your form has enctype='multipart/form-data'")
    print("2. Check that request.FILES is being properly accessed in your view")
    print("3. Verify that your model's ImageField is correctly configured")
    return True

if __name__ == "__main__":
    check_media_setup()
