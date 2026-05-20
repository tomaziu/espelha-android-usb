@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 "%~dp0phone_mirror.py"
) else (
    python "%~dp0phone_mirror.py"
)

if errorlevel 1 (
    echo.
    echo O programa fechou com erro.
    pause
)
