@echo off
cd /d "D:\Github Doc\AstrBotLauncher\bge-m3-embedded"
echo Starting uvicorn server on http://0.0.0.0:8000 ...
uvicorn main:app --host 0.0.0.0 --port 8000
pause
