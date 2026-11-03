@echo off
cd /d "%~dp0" || goto :error

python -m pip --version >nul 2>&1
if errorlevel 1 (
    python -m ensurepip --upgrade || goto :error
)

python -m pip install -r requirements.txt || goto :error
python -m streamlit run app.py || goto :error
exit /b 0

:error
echo.
echo Setup or launch failed. Check the error above.
pause
exit /b 1
