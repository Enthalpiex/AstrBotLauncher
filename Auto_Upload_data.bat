@echo off
setlocal

:: 切换到脚本目录
cd /d "D:\Github Doc\AstrBotLauncher\AstrBot"

:: 运行 Python 脚本
python batch_upload_files.py "D:\Github Doc\wikiextractor\Space_articles" --kb-name "Aerospace"

pause
