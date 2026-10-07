@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set OPENBLAS_NUM_THREADS=1
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
if not exist ".venv\Scripts\python.exe" (
    echo Prepare o ambiente .venv seguindo o README.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" src/baixar_ecg.py
if errorlevel 1 (
    pause
    exit /b 1
)
".venv\Scripts\python.exe" src/executar_ir_alem2.py
if errorlevel 1 (
    pause
    exit /b 1
)
pause
