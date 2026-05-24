@echo off
setlocal
cd /d "%~dp0"

python -m py_compile phone_mirror.py
if errorlevel 1 exit /b %errorlevel%

python -m unittest discover -s tests -v
