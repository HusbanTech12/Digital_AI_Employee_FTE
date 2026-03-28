@echo off
REM AI Employee - Setup Ollama (Free Local AI)
REM This script installs and configures Ollama for AI Employee

echo ============================================================
echo AI Employee - Ollama Setup (Free Local AI)
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.13+ from https://python.org
    pause
    exit /b 1
)

echo Step 1: Installing ollama Python package...
pip install ollama
if errorlevel 1 (
    echo WARNING: pip install failed. Trying with --user flag...
    pip install --user ollama
)
echo.

echo Step 2: Checking Ollama installation...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo Ollama is NOT installed!
    echo.
    echo Please install Ollama first:
    echo 1. Visit: https://ollama.com/download
    echo 2. Download and run the installer
    echo 3. Run this script again
    echo.
    pause
    exit /b 1
)

echo Ollama is installed!
echo.

echo Step 3: Downloading Qwen model (this may take a few minutes)...
echo Model: qwen2.5:7b (4GB)
echo.
ollama pull qwen2.5:7b
echo.

echo Step 4: Testing Ollama...
echo.
echo Running: ollama run qwen2.5:7b "Say hello in one sentence"
echo.
ollama run qwen2.5:7b "Say hello in one sentence"
echo.

echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Ollama is ready to use with AI Employee.
echo.
echo To process tasks with AI:
echo   cd scripts
echo   python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once
echo.
echo Or set environment variable for permanent use:
echo   set AI_PROVIDER=ollama
echo.
echo To use a different model:
echo   ollama pull qwen2.5:14b
echo   python orchestrator.py --vault ..\AI_Employee_Vault --ollama --model qwen2.5:14b --once
echo.
echo ============================================================
pause
