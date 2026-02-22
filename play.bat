@echo off
:: A Quiet Current — Windows launcher
:: Tries Python, then gives friendly instructions if not found.

title A Quiet Current

python --version >nul 2>&1
if %errorlevel% == 0 (
    python main.py
    goto end
)

py --version >nul 2>&1
if %errorlevel% == 0 (
    py main.py
    goto end
)

echo.
echo  A Quiet Current needs Python 3.10 or later.
echo.
echo  Download it free from: https://www.python.org/downloads/
echo  Make sure to check "Add Python to PATH" during installation.
echo.
echo  Then double-click play.bat again.
echo.
pause

:end
