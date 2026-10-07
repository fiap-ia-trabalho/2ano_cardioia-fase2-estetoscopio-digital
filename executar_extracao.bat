@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Prepare o ambiente .venv seguindo o README antes de executar a extracao.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" src\extracao_sintomas.py
pause
