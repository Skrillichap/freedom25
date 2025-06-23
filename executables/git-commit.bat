@echo off
cd /d %~dp0
git add .
git commit -m "Update from %COMPUTERNAME%"
pause
git add .
git commit -m "Checkpoint: Added chart plotting and exposure logic"

