@echo off
echo Building AlbumVision...

:: Create a new spec file for AlbumVision
echo Creating spec file...
pyinstaller --name AlbumVision ^
    --noconsole ^
    --icon "resources/icons/ab_logo.ico" ^
    --add-data "resources/icons;resources/icons" ^
    --add-data "data/test_images;data/test_images" ^
    --add-data "yolov8n.pt;." ^
    --hidden-import PySide6 ^
    --hidden-import cv2 ^
    --hidden-import numpy ^
    --hidden-import matplotlib ^
    --hidden-import ultralytics ^
    app/gui/main_window.py

echo Build complete!
echo Executable can be found in dist/AlbumVision folder
pause