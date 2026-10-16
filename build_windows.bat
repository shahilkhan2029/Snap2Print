@echo off
setlocal enabledelayedexpansion

echo ================================================================
echo           Snap2Print - Windows Standalone Executable Builder
echo ================================================================
echo.

:: Change to the repository root directory
cd /d "%~dp0"

:: Identify Python executable
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
    set "PYINSTALLER_EXE=.venv\Scripts\pyinstaller.exe"
    echo [OK] Using virtual environment Python: !PYTHON_EXE!
) else (
    set "PYTHON_EXE=python"
    set "PYINSTALLER_EXE=pyinstaller"
    echo [!] .venv not found. Using system Python...
)

:: Verify PyInstaller is installed
!PYTHON_EXE! -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [!] PyInstaller not found. Installing PyInstaller...
    !PYTHON_EXE! -m pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller. Please check your internet connection and Python setup.
        pause
        exit /b 1
    )
)

echo.
echo [*] Cleaning previous temporary build cache...
if exist "%TEMP%\snap2print_build" rmdir /s /q "%TEMP%\snap2print_build" 2>nul

echo [*] Starting PyInstaller build using Snap2Print.spec...
echo     Workpath: %TEMP%\snap2print_build
echo     Distpath: dist\Snap2Print
echo.

!PYTHON_EXE! -m PyInstaller Snap2Print.spec --workpath "%TEMP%\snap2print_build" --distpath dist -y

if errorlevel 1 (
    echo.
    echo [ERROR] PyInstaller build failed! Please check the log messages above.
    pause
    exit /b 1
)

:: Ensure runtime writable directories exist in the distribution
if not exist "dist\Snap2Print\input" mkdir "dist\Snap2Print\input"
if not exist "dist\Snap2Print\output" mkdir "dist\Snap2Print\output"
if not exist "dist\Snap2Print\logs" mkdir "dist\Snap2Print\logs"

echo.
echo ================================================================
echo [SUCCESS] Snap2Print standalone Windows application is built!
echo ================================================================
echo  Executable location:
echo    dist\Snap2Print\Snap2Print.exe
echo.
echo  To run:
echo    Double-click dist\Snap2Print\Snap2Print.exe
echo ================================================================
echo.
pause
