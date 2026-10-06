@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Prepare o ambiente .venv seguindo o README antes de abrir os notebooks.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m jupyterlab notebooks/
pause
