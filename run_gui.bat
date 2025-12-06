@echo off
set PYTHONPATH=%PYTHONPATH%;%~dp0
start "" pythonw app/gui/main.py
exit
