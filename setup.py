from setuptools import setup, find_packages
import subprocess
import sys
import os

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Function to set up the environment
def setup_environment():
    print("Setting up AlbumVision environment...")
    
    # Install required packages
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Create necessary directories
    directories = [
        'models',
        'user_data/thumbnails',
        'user_data/cache',
        'user_data/analytics',
        'user_data/exports'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("Environment setup complete!")

# Setup configuration
setup(
    name="AlbumVision",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
    author="Theo7973",
    author_email="theo-soliman@outlook.com",
    description="An image categorization and management application",
)

# Run environment setup if executed directly
if __name__ == "__main__":
    setup_environment()
