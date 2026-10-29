@echo off
rem Frostpunk Dev Menu - Windows launcher.
rem This file does NOT change the game. It only finds Python and starts dev_menu.py, which does
rem all the work. Without this file:   py -3 dev_menu.py   (or: python dev_menu.py)
setlocal
title Frostpunk Dev Menu
cd /d "%~dp0"

set "PY="
py -3 -c "import sys" >nul 2>&1 && set "PY=py -3"
if not defined PY python -c "import sys; sys.exit(sys.version_info[0] < 3)" >nul 2>&1 && set "PY=python"
if not defined PY goto nopython

%PY% "%~dp0dev_menu.py" %*
echo.
pause
exit /b

:nopython
echo This installer needs Python 3, which is not installed on this PC.
echo Python is free and safe; it is the language dev_menu.py is written in.
echo.
where winget >nul 2>&1 || goto manual
choice /c YN /m "Install Python now (runs: winget install Python.Python.3.13)"
if errorlevel 2 goto manual
winget install -e --id Python.Python.3.13 --accept-source-agreements --accept-package-agreements
echo.
echo Done. Close this window and double-click "Install Dev Menu (Windows).bat" again.
pause
exit /b

:manual
echo Download Python from https://www.python.org/downloads/windows/
echo During setup, tick "Add python.exe to PATH". Then double-click this file again.
start "" https://www.python.org/downloads/windows/
pause
