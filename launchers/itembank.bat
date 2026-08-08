@echo off
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
if errorlevel 1 (
    echo itembank needs Python 3.11 or newer. Install it from https://python.org and run this file again.
    pause
    exit /b 1
)
py -3 "%~dp0itembank.pyz" %*
exit /b %errorlevel%
