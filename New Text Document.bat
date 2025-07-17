@echo off
REM Build Album Vision+ Executable
REM Double-click this file to build your app

echo ============================================
echo   ALBUM VISION+ EXECUTABLE BUILDER
echo ============================================
echo.

REM Check if Python is available
python --version nul 2&1
if errorlevel 1 (
    echo ERROR Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit b 1
)

echo Python is available
echo.

REM Install PyInstaller if needed
echo Installingupdating PyInstaller...
python -m pip install pyinstaller --upgrade
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist dist rmdir s q dist
if exist build rmdir s q build
if exist .spec del .spec
echo.

REM Build the executable directly from your main window
echo Building Album Vision+ executable...
echo This may take 5-10 minutes...
echo.

pyinstaller ^
    --onefile ^
    --windowed ^
    --name=Album Vision+ ^
    --distpath=dist ^
    --workpath=build ^
    --clean ^
    --add-data=app;app ^
    --add-data=data;data ^
    --hidden-import=ultralytics ^
    --hidden-import=torch ^
    --hidden-import=torchvision ^
    --hidden-import=cv2 ^
    --hidden-import=PySide6 ^
    --hidden-import=PySide6.QtCore ^
    --hidden-import=PySide6.QtGui ^
    --hidden-import=PySide6.QtWidgets ^
    --hidden-import=numpy ^
    --hidden-import=PIL ^
    --hidden-import=sqlite3 ^
    --hidden-import=aiosqlite ^
    --hidden-import=app.utils.Auto_Sort_Basic ^
    --hidden-import=app.utils.file_utils ^
    --hidden-import=app.utils.image_quality ^
    --hidden-import=app.utils.path_settings ^
    --hidden-import=app.gui.widgets.yolo_results_widget ^
    --hidden-import=db_utils ^
    main_window.py

if errorlevel 1 (
    echo.
    echo ============================================
    echo   BUILD FAILED!
    echo ============================================
    echo Please check the error messages above
    echo Common issues
    echo - Missing dependencies pip install -r requirements.txt
    echo - Wrong directory ensure you're in the AlbumVision folder
    echo - Missing main_window.py file
    pause
    exit b 1
)

echo.
echo ============================================
echo   BUILD COMPLETED SUCCESSFULLY!
echo ============================================
echo.

REM Check if executable was created
if exist distAlbum Vision+.exe (
    echo ✓ Album Vision+.exe created successfully!
    echo Location %CD%distAlbum Vision+.exe
    
    REM Get file size
    for %%A in (distAlbum Vision+.exe) do (
        echo Size %%~zA bytes
    )
    
    echo.
    echo Your Album Vision+ app is ready!
    echo.
    echo Next steps
    echo 1. Test the executable in the dist folder
    echo 2. Copy Album Vision+.exe to wherever you want
    echo 3. The app includes everything needed to run
    
) else (
    echo ✗ Executable not found in dist folder
    echo Build may have failed - check messages above
)

echo.
echo Press any key to exit...
pause nul