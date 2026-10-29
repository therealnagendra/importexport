@echo off
setlocal
cd /d "%~dp0"
set /p backup_file="Enter backup database file path: "
if not exist "%backup_file%" (
    echo Backup file not found.
    exit /b 1
)
set /p confirm="This will overwrite the current database. Continue? (y/N): "
if /I not "%confirm%"=="y" (
    echo Restore cancelled.
    exit /b 0
)
copy /y "%backup_file%" "instance\import_export.db"
if exist backups\uploads\ (
    robocopy backups\uploads uploads /E >nul
)

echo Restore complete.
