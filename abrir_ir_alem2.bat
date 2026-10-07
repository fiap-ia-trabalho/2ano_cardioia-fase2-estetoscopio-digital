@echo off
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
".venv\Scripts\python.exe" -m jupyterlab notebooks/03_diagnostico_visual.ipynb
pause
