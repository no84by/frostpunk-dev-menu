@echo off
rem Frostpunk Dev Menu - Windows launcher.
rem This file does NOT change the game. It only finds Python and starts dev_menu.py, which does
rem all the work. Without this file:   py -3 dev_menu.py   (or: python dev_menu.py)
rem If Python is missing it can start the official Python installer; you approve it yourself.
setlocal
title Frostpunk Dev Menu
cd /d "%~dp0"
set "PY_VER=3.13.16"

call :findpy
if not defined PY goto nopython
:run
%PY% "%~dp0dev_menu.py" %*
echo.
pause
exit /b

:findpy
set "PY="
py -3 -c "import sys" >nul 2>&1 && set "PY=py -3" && exit /b
python -c "import sys; sys.exit(sys.version_info[0] < 3)" >nul 2>&1 && set "PY=python" && exit /b
rem freshly installed Python is not on this window's PATH yet: look in the usual folders
for %%P in ("%LOCALAPPDATA%\Programs\Python\Launcher\py.exe" "%WINDIR%\py.exe") do (
  if exist "%%~P" set "PY="%%~P" -3" && exit /b
)
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*" "%ProgramFiles%\Python3*") do (
  if exist "%%~D\python.exe" set "PY="%%~D\python.exe""
)
exit /b

:nopython
echo This installer needs Python 3, which is not installed on this PC.
echo Python is free; the official installer comes from python.org.
echo.
choice /c YN /m "Install Python now"
if errorlevel 2 goto manual
where winget >nul 2>&1 && (
  echo Installing with winget. Approve the Windows prompt if one appears...
  winget install -e --id Python.Python.3.13 --accept-source-agreements --accept-package-agreements
) || call :download
call :findpy
if defined PY goto run
echo.
echo Python did not install. Try again, or install it from python.org (link below).

:manual
echo Download Python from https://www.python.org/downloads/windows/
echo During setup, tick "Add python.exe to PATH". Then double-click this file again.
start "" https://www.python.org/downloads/windows/
pause
exit /b

:download
set "ARCH=amd64"
if /i "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "ARCH=arm64"
set "PYSETUP=%TEMP%\python-%PY_VER%-%ARCH%.exe"
echo Downloading the Python installer from python.org...
curl.exe -fL -o "%PYSETUP%" "https://www.python.org/ftp/python/%PY_VER%/python-%PY_VER%-%ARCH%.exe" || exit /b
powershell -NoProfile -Command "if ((Get-AuthenticodeSignature '%PYSETUP%').SignerCertificate.Subject -notmatch 'Python Software Foundation') { exit 1 }" || (
  echo The download is not signed by the Python Software Foundation; not running it.
  exit /b
)
echo Click "Install Now" in the Python window that opens...
start /wait "" "%PYSETUP%" PrependPath=1
exit /b
