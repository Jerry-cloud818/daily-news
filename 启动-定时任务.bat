@echo off
chcp 65001 >nul
echo ========================================
echo       每日新闻速递 - 定时模式
echo           每天22:00自动更新
echo ========================================
echo.
cd /d "%~dp0"
python main.py --schedule
pause
