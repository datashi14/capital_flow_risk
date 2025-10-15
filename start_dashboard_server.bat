@echo off
echo ===========================================
echo Starting Capital Flow & Credit Risk Dashboard
echo ===========================================
echo.

cd /d %~dp0

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.11+ from: https://www.python.org/downloads/
    echo Make sure to check 'Add to PATH' during installation
    pause
    exit /b 1
)

echo.
echo Checking dependencies...
pip list | findstr streamlit >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting dashboard...
echo ===========================================
echo.
echo Dashboard will be available at:
echo   Local:      http://localhost:8501
echo   Network:    http://your-server-ip:8501
echo   External:   http://37.187.250.eu:8501
echo.
echo Press Ctrl+C to stop the dashboard
echo ===========================================
echo.

streamlit run dashboards/streamlit_app.py --server.address 0.0.0.0 --server.port 8501

pause

