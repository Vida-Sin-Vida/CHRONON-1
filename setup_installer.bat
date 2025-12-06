
@echo off
echo ===========================================
echo   CHRONON Installer (Windows)
echo ===========================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.9+ and add to PATH.
    pause
    exit /b
)

:: 2. Create Venv
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
) else (
    echo [INFO] Virtual environment exists.
)

:: 3. Install Wheel
echo [INFO] Installing CHRONON...
call venv\Scripts\activate
pip install --upgrade pip
pip install . 
:: Or install specific wheel if built

:: 4. Create Shortcut
echo [INFO] Creating Desktop Shortcut...
set SCRIPT="%TEMP%\CreateShortcut.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo sLinkFile = "%USERPROFILE%\Desktop\CHRONON.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%~dp0venv\Scripts\pythonw.exe" >> %SCRIPT%
echo oLink.Arguments = "-m app.main" >> %SCRIPT%
echo oLink.WorkingDirectory = "%~dp0" >> %SCRIPT%
echo oLink.Description = "CHRONON Scientific Application" >> %SCRIPT%
echo oLink.IconLocation = "%~dp0app\assets\icon.ico" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%
cscript /nologo %SCRIPT%
del %SCRIPT%

echo.
echo [SUCCESS] Installation Complete!
echo You can run the app from the Desktop shortcut 'CHRONON'.
pause
