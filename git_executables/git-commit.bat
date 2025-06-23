@echo off
cd /d %~dp0..
git add .
git commit -m "Update project files"
git push origin main
pause
