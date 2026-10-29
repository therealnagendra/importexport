@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found. Please install Python 3.11 or newer and try again.
    exit /b 1
)
if not exist .venv (
    python -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -c "import flask, pytest, werkzeug; print('Dependencies verified')"
python app.py init-db
if errorlevel 1 (
    echo Setup finished with errors. Review the log and fix the issue.
    exit /b 1
)
echo Setup completed successfully.
echo Run start.bat to launch the project.
