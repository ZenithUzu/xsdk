@echo off
cd /d "%~dp0"
py -3 -c "import tkinter" >nul 2>&1
if not errorlevel 1 (
    py -3 tools\windows\gui.py
    goto :done
)
if exist "C:\msys64\ucrt64\bin\python.exe" (
    set "PATH=C:\msys64\ucrt64\bin;%PATH%"
    "C:\msys64\ucrt64\bin\python.exe" tools\windows\gui.py
    goto :done
)
echo Install Python 3.11+ with tkinter and the py launcher.
echo Instala Python 3.11+ con tkinter y el lanzador py.
echo Instale Python 3.11+ com tkinter e o inicializador py.
echo https://www.python.org/downloads/windows/
pause
exit /b 1
:done
if errorlevel 1 pause
