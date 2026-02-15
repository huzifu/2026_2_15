@echo off
echo ========================================
echo AI 智能教学助手系统 - 安装脚本
echo ========================================
echo.

echo 正在检查 Python 环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo.
echo 正在安装依赖包...
python -m pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo 警告: 部分依赖安装失败，但系统可能仍可运行
    echo 如果遇到问题，请手动安装缺失的包
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 运行方式:
echo   python main.py
echo.
echo 默认账号:
echo   管理员: admin / admin123
echo   教师: teacher1 / 123456
echo   学生: student1 / 123456
echo.
pause
