@echo off
cd /d %~dp0\..

:: Prompt for commit message inline
set /p message="Enter commit message: "
git add .
git commit -m "%message%"
git push origin main

pause
