@echo off
chcp 65001 >nul
echo ============================================================
echo 安全帽检测系统 - 环境配置脚本
echo ============================================================
echo.

:: 检查 Python 版本
echo [1/4] 检查 Python 版本...
python --version
echo.

:: 删除旧的虚拟环境（如果存在）
if exist venv (
    echo [2/4] 删除旧的虚拟环境...
    rmdir /s /q venv
    echo ✓ 旧环境已删除
) else (
    echo [2/4] 跳过（无旧环境）
)
echo.

:: 创建新的虚拟环境
echo [3/4] 创建新的虚拟环境...
python -m venv venv
if errorlevel 1 (
    echo ✗ 虚拟环境创建失败
    pause
    exit /b 1
)
echo ✓ 虚拟环境创建成功
echo.

:: 激活虚拟环境并安装依赖
echo [4/4] 安装依赖包...
call venv\Scripts\activate.bat

echo.
echo 升级 pip...
python -m pip install --upgrade pip -q

echo.
echo 安装核心依赖...
echo   - PyTorch (CPU版本)...
pip install torch==2.2.0 torchvision==0.17.0 --index-url https://download.pytorch.org/whl/cpu -q

echo   - PyQt5...
pip install PyQt5==5.15.10 -q

echo   - OpenCV...
pip install opencv-python==4.10.0.84 -q

echo   - 数据处理...
pip install numpy pandas -q

echo   - 可视化...
pip install matplotlib seaborn -q

echo   - YOLOv5 依赖...
pip install ultralytics scipy tqdm tensorboard pyyaml -q

echo.
echo ============================================================
echo ✓ 环境配置完成！
echo ============================================================
echo.
echo 测试安装:
python -c "import torch; import cv2; from PyQt5 import QtCore; print('✓ 所有依赖已安装')"

echo.
echo 下一步:
echo   1. 运行测试: python test_detector.py
echo   2. 启动应用: python app\main.py
echo.
echo 虚拟环境激活命令:
echo   venv\Scripts\activate.bat
echo.
pause







