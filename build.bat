@echo off
REM Windows构建脚本

echo 正在启动构建脚本...
python build_script.py
if %ERRORLEVEL% neq 0 (
    echo 构建失败！
    pause
    exit /b 1
)
pause 