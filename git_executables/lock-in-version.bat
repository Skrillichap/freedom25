@echo off
cd /d %~dp0..
git add .
git commit -m "Final commit for V0.3"
git tag v0.3
git push origin main --tags
pause
