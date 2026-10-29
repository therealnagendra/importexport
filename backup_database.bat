@echo off
setlocal
cd /d "%~dp0"
if not exist instance\import_export.db (
    echo Database not found. Nothing to back up.
    exit /b 1
)
set timestamp=%date:~-4,4%-%date:~-10,2%-%date:~-7,2%_%time:~0,2%-%time:~3,2%-%time:~6,2%
set timestamp=%timestamp: =0%
if not exist backups mkdir backups
copy /y "instance\import_export.db" "backups\import_export_%timestamp%.db"
if exist uploads\ (
    robocopy uploads backups\uploads /E >nul
)

echo Backup created in backups\
