@echo off
cd /d %~dp0..
git add .
git commit -m "Final commit for V0.5"
git tag v0.5
git push origin main --tags
pause
