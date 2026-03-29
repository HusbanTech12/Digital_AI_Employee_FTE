@echo off
REM Test Silver Tier Ollama Integration
REM This script tests the complete Ollama + Qwen-Agent integration

echo ============================================================
echo Silver Tier: Ollama + Qwen-Agent Integration Test
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Run the test
echo Running integration tests...
echo.
cd scripts
python test_ollama_integration.py

echo.
echo ============================================================
echo Test Complete
echo ============================================================
echo.
echo If you see failures related to "model not found":
echo   1. Install Ollama: https://ollama.com/download
echo   2. Download model: ollama pull qwen2.5:7b
echo.
echo If tests pass, you're ready to use Silver Tier!
echo.
pause
