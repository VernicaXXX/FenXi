@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo Code Analyzer - 本地代码分析器
echo ============================================
echo.
echo 命令用法:
echo   project ^<路径^>    - 分析整个项目
echo   file ^<文件路径^>   - 解析单个文件
echo   tree ^<路径^>       - 显示目录树
echo   help                - 显示帮助
echo   exit                - 退出
echo.
python cli.py
pause