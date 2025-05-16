# AlbumVision

## Introduction
AlbumVision is an intelligent desktop photo organization application that combines YOLO11 object detection with computer vision techniques to automatically categorize and manage large image collections. This tool helps users efficiently organize photos based on content, quality, and custom categories without requiring manual tagging. 

Whether you're a professional photographer with thousands of photos or just someone looking to bring order to your family photo collection, AlbumVision streamlines the process by automatically detecting image content and creating an organized folder structure on your local machine.

## Features
* **Automatic image categorization** using state-of-the-art YOLO11 object detection
* **Smart quality assessment** that identifies and filters blurry or low-quality images
* **Dimension-aware processing** that adapts quality thresholds to different image sizes
* **Custom category management** allowing users to add or remove folder categories
* **Tag organization** with hierarchical structure
* **Powerful analytics** on your image collection
* **Duplicate detection** to eliminate redundant photos
* **Flexible organization options** with path selection and persistent settings
* **Non-destructive workflow** that preserves original image files
* **Desktop application** with intuitive user interface for Windows, macOS, and Linux

## Technologies
AlbumVision leverages several cutting-edge technologies:

* **Python 3.11.9** - Core programming language
* **YOLO11 (ultralytics-v11)** - State-of-the-art object detection for image categorization
* **OpenCV** - Computer vision operations including blur detection
* **PySide6** - Modern Qt-based GUI framework for desktop application
* **PyTorch/TorchVision** - Deep learning framework supporting YOLO11
* **NumPy/Pandas** - Data processing and analysis
* **JSON** - Configuration and settings storage
* **Git/GitHub** - Version control and collaborative development

## Installation

### Prerequisites
* Python 3.11.9 (recommended) or Python 3.8-3.11
* Git
* 4GB+ RAM recommended for optimal YOLO11 performance
* GPU support recommended but not required

### End-User Setup
1. Download the latest release from the [Releases page](https://github.com/Theo7973/AlbumVision/releases)
   - Windows: Download `AlbumVision-Setup-x64.exe` and run the installer
   - macOS: Download `AlbumVision-x64.dmg`, open it, and drag to Applications
   - Linux: Download `AlbumVision-x64.AppImage` and make it executable

Alternatively, you can install from source:

1. Clone the repository:
```bash
git clone https://github.com/Theo7973/AlbumVision.git
cd AlbumVision
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -e .
```

4. Run the application:
```bash
python main.py
```

The YOLO11 model will be downloaded automatically on first run.

## Development Setup
For developers looking to contribute to AlbumVision, follow these additional steps:

1. Fork the repository on GitHub and clone your fork:
```bash
git clone https://github.com/YOUR-USERNAME/AlbumVision.git
cd AlbumVision
```

2. Set up the development environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # macOS/Linux
pip install -e .
pip install pytest pytest-cov flake8  # Developer tools
```

3. Create the necessary directory structure (if not already present):
```bash
mkdir -p app/utils/model_downloader
mkdir -p data/test_images
mkdir -p tests
mkdir -p user_data
```

4. Run tests to verify the setup:
```bash
python tests/test_quality.py
python tests/test_folders.py
python tests/test_path_settings.py
```

5. Build process:
   - No compilation needed as AlbumVision is a Python application
   - To create executable for distribution:
     ```bash
     pip install pyinstaller
     pyinstaller --windowed --onefile --name AlbumVision main.py
     ```
   - The executable will be in the `dist` folder
   - To contribute, create a feature branch, make your changes, and submit a pull request
   - Follow the existing code style and add tests for new features

## Project Structure
```
AlbumVision/
├── app/
│   ├── gui/               # User interface components
│   ├── categorizer/       # Image categorization using YOLO11
│   ├── database/          # Data storage and management
│   └── utils/             # Utility functions
│       ├── image_quality.py       # Image quality assessment
│       ├── folder_manager.py      # Folder creation and management
│       ├── path_settings.py       # Path and settings storage
│       └── model_downloader/      # YOLO11 model management
├── data/
│   └── test_images/       # Sample images for testing
├── models/                # Downloaded ML models
├── tests/                 # Test scripts
├── user_data/             # User settings and cached data
├── main.py                # Application entry point
├── requirements.txt       # Package dependencies
├── setup.py               # Installation script
└── README.md              # Project documentation
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributors
- Theo Soliman- Dev
- Austin Barlow -Dev
- Chun Yu  - Dev
- Eli'Sha Leonard- Dev

## Project Status
AlbumVision is currently in **Beta** stage. Core functionality is implemented and working, but some features are still being refined and optimized. The application is usable but may contain bugs or performance issues.

## Known Issues
- High memory usage when processing large image collections
- Occasional false positives in blur detection for artistic photos
- Limited support for RAW image formats
- GUI may become unresponsive while processing large batches
- Some display scaling issues on high-DPI monitors
- Requires manual refresh after folder changes in some cases

## Roadmap
- [ ] Implement batch processing for large image collections
- [ ] Add multi-language support
- [ ] Create detailed analytics dashboard
- [ ] Add face recognition capabilities
- [ ] Develop cloud sync feature
- [ ] Add platform-specific installers for easier distribution
- [ ] Implement drag-and-drop interface for image importing

## Support
For questions or issues, please:
- Open an issue on the [GitHub Issues page](https://github.com/Theo7973/AlbumVision/issues)
- Contact the development team at [theo-soliman@outlook.com](mailto:theo-soliman@outlook.com)

## Code Examples
Here's a simple example of how to use the image quality detection:

```python
from app.utils.image_quality import check_image_quality

# Check if an image is high quality
quality, score, dimensions = check_image_quality("path/to/image.jpg")
print(f"Image quality: {quality}, Score: {score}, Dimensions: {dimensions}")
```

Creating category folders:
```python
from app.utils.folder_manager import create_output_folders

# Define categories and create folders
categories = ["Landscapes", "Portraits", "Animals", "Food"]
folder_paths = create_output_folders(categories, "path/to/output")
```
