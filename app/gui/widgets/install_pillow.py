# install_pillow.py
# Run this script to install the required library for resize functionality

import subprocess
import sys

def install_pillow():
    """Install PIL/Pillow library for image processing"""
    try:
        print("Installing Pillow library for image resize functionality...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        print("✅ Pillow installed successfully!")
        
        # Test the installation
        try:
            from PIL import Image
            print("✅ Pillow is working correctly!")
            print("You can now use the resize functionality in AlbumVision+")
            return True
        except ImportError:
            print("❌ Pillow installation failed - please install manually")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Pillow: {e}")
        print("Please try installing manually with: pip install Pillow")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("AlbumVision+ Resize Feature Setup")
    print("=" * 40)
    
    # Check if Pillow is already installed
    try:
        from PIL import Image
        print("✅ Pillow is already installed!")
    except ImportError:
        print("Pillow not found. Installing...")
        install_pillow()
    
    input("\nPress Enter to continue...")