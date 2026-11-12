@echo off
setlocal
title ChronosMatch Launcher

REM Always run from the folder containing this script.
cd /d "%~dp0"

set "VENV_PY=%~dp0.venv\Scripts\python.exe"

echo.
echo ==========================================
echo        CHRONOSMATCH - PROJECT LAUNCHER
echo ==========================================
echo.

REM Create the virtual environment on the first run.
if not exist "%VENV_PY%" (
    echo [1/4] Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 goto :error
) else (
    echo [1/4] Virtual environment found.
)

REM Install or verify backend and frontend dependencies.
echo [2/4] Checking backend dependencies...
"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo [3/4] Checking dashboard dependencies...
"%VENV_PY%" -m pip install -r frontend\requirements.txt
if errorlevel 1 goto :error

REM Start the backend in its own terminal window.
echo [4/4] Starting ChronosMatch services...
start "ChronosMatch Backend" cmd /k ""%VENV_PY%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

REM Give the API a moment to initialize before starting the dashboard.
timeout /t 3 /nobreak >nul

REM Start the Streamlit dashboard in a second terminal window.
start "ChronosMatch Dashboard" cmd /k ""%VENV_PY%" -m streamlit run frontend\dashboard.py"

echo.
echo ChronosMatch is starting.
echo Dashboard: http://localhost:8501
echo API docs:  http://127.0.0.1:8000/docs
echo.
echo Keep both service windows open while using the application.
echo Close those windows to stop the services.
echo.
pause
exit /b 0

:error
echo.
echo ERROR: Setup or startup failed.
echo Check the messages above. Make sure Python is installed and available in PATH.
pause
exit /b 1
