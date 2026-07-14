@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo Code Analyzer - 本地代码分析器
echo ============================================
echo.
python cli.py
pause