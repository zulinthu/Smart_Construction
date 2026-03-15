@echo off
REM ========================================
REM 安全帽检测系统 - Windows构建脚本
REM 类似CMake的项目构建管理
REM ========================================

setlocal EnableDelayedExpansion

REM 颜色定义（Windows 10+）
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "NC=[0m"

if "%~1"=="" goto :help

REM 命令分发
if /i "%~1"=="help" goto :help
if /i "%~1"=="init" goto :init
if /i "%~1"=="install" goto :install
if /i "%~1"=="install-dev" goto :install_dev
if /i "%~1"=="setup-yolov5" goto :setup_yolov5
if /i "%~1"=="download-weights" goto :download_weights
if /i "%~1"=="build" goto :build
if /i "%~1"=="clean" goto :clean
if /i "%~1"=="clean-all" goto :clean_all
if /i "%~1"=="run" goto :run
if /i "%~1"=="gui" goto :gui
if /i "%~1"=="train-baseline" goto :train_baseline
if /i "%~1"=="train-improved" goto :train_improved
if /i "%~1"=="eval" goto :eval
if /i "%~1"=="compare" goto :compare
if /i "%~1"=="test" goto :test
if /i "%~1"=="test-camera" goto :test_camera
if /i "%~1"=="format" goto :format
if /i "%~1"=="lint" goto :lint
if /i "%~1"=="tensorboard" goto :tensorboard
if /i "%~1"=="info" goto :info
if /i "%~1"=="check-env" goto :check_env
if /i "%~1"=="all" goto :all

echo %RED%错误：未知命令 "%~1"%NC%
echo 运行 'build.bat help' 查看帮助
exit /b 1

:help
echo.
echo %BLUE%========================================%NC%
echo %GREEN%  安全帽检测系统 - 构建系统%NC%
echo %BLUE%========================================%NC%
echo.
echo 使用方法: build.bat [command]
echo.
echo %YELLOW%环境设置:%NC%
echo   init              - 初始化项目（首次使用）
echo   install           - 安装所有依赖
echo   install-dev       - 安装开发依赖
echo   setup-yolov5      - 下载并配置YOLOv5
echo   download-weights  - 下载预训练权重
echo.
echo %YELLOW%项目构建:%NC%
echo   build             - 构建项目
echo   clean             - 清理临时文件
echo   clean-all         - 深度清理（包括虚拟环境）
echo.
echo %YELLOW%运行程序:%NC%
echo   run               - 运行主程序
echo   gui               - 启动GUI界面
echo.
echo %YELLOW%训练与评估:%NC%
echo   train-baseline    - 训练基线模型
echo   train-improved    - 训练改进模型
echo   eval              - 评估模型
echo   compare           - 对比模型性能
echo.
echo %YELLOW%测试:%NC%
echo   test              - 运行测试
echo   test-camera       - 测试摄像头
echo.
echo %YELLOW%代码质量:%NC%
echo   format            - 格式化代码
echo   lint              - 代码检查
echo.
echo %YELLOW%工具:%NC%
echo   tensorboard       - 启动TensorBoard
echo   info              - 显示项目信息
echo   check-env         - 检查环境配置
echo.
echo %YELLOW%快速开始:%NC%
echo   all               - 一键安装所有内容
echo.
exit /b 0

:init
echo %GREEN%>>> 初始化项目环境...%NC%
python -m venv venv
echo %GREEN%>>> 虚拟环境创建完成%NC%
echo %YELLOW%>>> 请运行: build.bat install%NC%
exit /b 0

:install
echo %GREEN%>>> 安装项目依赖...%NC%
python -m pip install --upgrade pip
pip install -r requirements.txt
python config.py
echo %GREEN%>>> 依赖安装完成！%NC%
exit /b 0

:install_dev
echo %GREEN%>>> 安装开发依赖...%NC%
pip install black flake8 pytest pytest-cov
echo %GREEN%>>> 开发依赖安装完成！%NC%
exit /b 0

:setup_yolov5
echo %GREEN%>>> 下载YOLOv5源码...%NC%
if not exist "models\yolov5" (
    cd models
    git clone https://github.com/ultralytics/yolov5.git
    cd yolov5
    pip install -r requirements.txt
    cd ..\..
    echo %GREEN%>>> YOLOv5配置完成！%NC%
) else (
    echo %YELLOW%YOLOv5已存在，跳过下载%NC%
)
exit /b 0

:download_weights
echo %GREEN%>>> 下载预训练权重...%NC%
if not exist "models\weights" mkdir models\weights
python -c "import urllib.request; urllib.request.urlretrieve('https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt', 'models/weights/yolov5s.pt')"
echo %GREEN%>>> 权重下载完成！%NC%
exit /b 0

:build
echo %GREEN%>>> 构建项目...%NC%
call :install
python setup.py develop
echo %GREEN%>>> 项目构建完成！%NC%
exit /b 0

:clean
echo %YELLOW%>>> 清理临时文件...%NC%
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul
for /d /r %%d in (*.egg-info) do @if exist "%%d" rd /s /q "%%d"
if exist "build" rd /s /q build
if exist "dist" rd /s /q dist
if exist ".pytest_cache" rd /s /q .pytest_cache
echo %GREEN%>>> 清理完成！%NC%
exit /b 0

:clean_all
echo %RED%>>> 深度清理...%NC%
call :clean
if exist "venv" rd /s /q venv
if exist "results\experiments" rd /s /q results\experiments
echo %GREEN%>>> 深度清理完成！%NC%
exit /b 0

:run
python run.py
exit /b 0

:gui
echo %GREEN%>>> 启动GUI界面...%NC%
python app/main.py
exit /b 0

:train_baseline
echo %GREEN%>>> 训练基线模型...%NC%
python train/train_baseline.py --data data/helmet.yaml --weights models/weights/yolov5s.pt --epochs 100 --batch-size 16
exit /b 0

:train_improved
echo %GREEN%>>> 训练改进模型...%NC%
python train/train_improved.py --data data/helmet.yaml --epochs 100 --batch-size 16
exit /b 0

:eval
echo %GREEN%>>> 评估模型...%NC%
python evaluate/eval_model.py --weights models/weights/improved_final.pt --data data/helmet.yaml
exit /b 0

:compare
echo %GREEN%>>> 对比模型性能...%NC%
python evaluate/compare_models.py
exit /b 0

:test
echo %GREEN%>>> 运行测试...%NC%
python -m pytest tests/ -v
exit /b 0

:test_camera
echo %GREEN%>>> 测试摄像头...%NC%
python -c "from app.utils.video_utils import test_camera, get_camera_list; cameras = get_camera_list(); print(f'可用摄像头: {cameras}'); test_camera(cameras[0], 5) if cameras else print('无摄像头')"
exit /b 0

:format
echo %GREEN%>>> 格式化代码...%NC%
python -m black . --exclude="/(\.git|venv|models/yolov5)/"
echo %GREEN%>>> 代码格式化完成！%NC%
exit /b 0

:lint
echo %GREEN%>>> 代码检查...%NC%
python -m flake8 . --exclude=venv,models/yolov5 --max-line-length=100
exit /b 0

:tensorboard
echo %GREEN%>>> 启动TensorBoard...%NC%
tensorboard --logdir results/experiments --port 6006
exit /b 0

:info
echo.
echo %BLUE%========================================%NC%
echo %GREEN%  项目信息%NC%
echo %BLUE%========================================%NC%
echo 项目名称: helmet-detection
python --version
pip --version
echo 工作目录: %CD%
echo %BLUE%========================================%NC%
exit /b 0

:check_env
echo %GREEN%>>> 检查环境配置...%NC%
python -c "import sys; print(f'Python: {sys.version}')"
python -c "import torch; print(f'PyTorch: {torch.__version__}')" 2>nul || echo PyTorch: 未安装
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')" 2>nul || echo CUDA: 未安装
python -c "import cv2; print(f'OpenCV: {cv2.__version__}')" 2>nul || echo OpenCV: 未安装
python -c "from PyQt5.QtCore import QT_VERSION_STR; print(f'PyQt5: {QT_VERSION_STR}')" 2>nul || echo PyQt5: 未安装
exit /b 0

:all
echo %GREEN%>>> 一键安装所有内容...%NC%
call :init
call :install
call :setup_yolov5
call :download_weights
echo %GREEN%>>> 项目配置完成！%NC%
echo %YELLOW%>>> 运行 'build.bat gui' 启动应用%NC%
exit /b 0










