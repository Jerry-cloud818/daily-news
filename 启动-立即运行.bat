@echo off
chcp 65001 >nul
echo ========================================
echo       每日新闻速递 - 立即执行
echo ========================================
echo.
cd /d "%~dp0"
python main.py
pause
