@echo off
REM WorkBuddy Launcher Script for Windows
REM This script helps launch WorkBuddy with proper environment setup

echo ===============================================
echo    WorkBuddy - Employee Wellness Tracker
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "workbuddy_env" (
    echo Creating virtual environment...
    python -m venv workbuddy_env
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call workbuddy_env\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo WARNING: Some dependencies may not have installed correctly
    echo Continuing anyway...
)

REM Launch WorkBuddy
echo.
echo Starting WorkBuddy...
echo.
python main.py

REM Deactivate virtual environment when done
deactivate

echo.
echo WorkBuddy has stopped.
pause 