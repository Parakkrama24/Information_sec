@echo off
echo ========================================
echo Secure V2I Communication Dashboard
echo ========================================
echo.
echo Starting API Server...
echo.

REM Start the API server
start "V2I API Server" cmd /k python api_server.py

REM Wait a moment for the server to start
timeout /t 3 /nobreak >nul

REM Open the dashboard in default browser
echo Opening dashboard in browser...
start UI\index.html

echo.
echo ========================================
echo Dashboard is now running!
echo ========================================
echo.
echo API Server: http://localhost:5000
echo Dashboard: UI\index.html (opened in browser)
echo.
echo To stop: Close the "V2I API Server" window
echo ========================================
