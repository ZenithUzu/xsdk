@echo off
cd /d "%~dp0"
py -3 tools\windows\gui.py
if errorlevel 1 (
  echo Instala Python 3.11 o posterior de 64 bits con tkinter y el lanzador py.
  echo https://www.python.org/downloads/windows/
  pause
)
