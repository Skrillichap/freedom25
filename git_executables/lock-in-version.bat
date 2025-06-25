@echo off
cd /d %~dp0..
git add .
git commit -m "Final commit for V0.2"
git tag v0.2
git push origin main --tags
pause
