@echo off
cd %~dp0
start cmd /k "pyinstaller --onefile --add-data "share.png;." --add-data "layout.css;." POsaver.py"
