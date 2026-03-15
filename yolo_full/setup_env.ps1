# PowerShell 环境配置脚本
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "安全帽检测系统 - 环境配置" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查 Python 版本
Write-Host "[1/4] 检查 Python 版本..." -ForegroundColor Green
python --version
Write-Host ""

# 2. 删除旧虚拟环境
if (Test-Path "venv") {
    Write-Host "[2/4] 删除旧虚拟环境..." -ForegroundColor Green
    Remove-Item -Recurse -Force venv
    Write-Host "✓ 旧环境已删除" -ForegroundColor Green
} else {
    Write-Host "[2/4] 跳过 (无旧环境)" -ForegroundColor Gray
}
Write-Host ""

# 3. 创建虚拟环境
Write-Host "[3/4] 创建虚拟环境..." -ForegroundColor Green
python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ 虚拟环境创建失败" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "✓ 虚拟环境创建成功" -ForegroundColor Green
Write-Host ""

# 4. 安装依赖
Write-Host "[4/4] 安装依赖..." -ForegroundColor Green
& "venv\Scripts\python.exe" -m pip install --upgrade pip --quiet

Write-Host "  安装 PyTorch (CPU版本)..." -ForegroundColor Cyan
& "venv\Scripts\pip.exe" install torch==2.2.0 torchvision==0.17.0 --index-url https://download.pytorch.org/whl/cpu --quiet

Write-Host "  安装 PyQt5..." -ForegroundColor Cyan
& "venv\Scripts\pip.exe" install PyQt5==5.15.10 --quiet

Write-Host "  安装 OpenCV..." -ForegroundColor Cyan
& "venv\Scripts\pip.exe" install opencv-python==4.10.0.84 --quiet

Write-Host "  安装数据处理库..." -ForegroundColor Cyan
& "venv\Scripts\pip.exe" install numpy pandas --quiet

Write-Host "  安装可视化库..." -ForegroundColor Cyan
& "venv\Scripts\pip.exe" install matplotlib seaborn --quiet

Write-Host "  安装 YOLOv5 依赖..." -ForegroundColor Cyan
& "venv\Scripts\pip.exe" install ultralytics scipy tqdm tensorboard pyyaml --quiet

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "✓ 环境配置完成！" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 测试安装
Write-Host "测试安装..." -ForegroundColor Yellow
& "venv\Scripts\python.exe" -c "import torch; import cv2; from PyQt5 import QtCore; print('✓ 所有依赖已安装')"

Write-Host ""
Write-Host "下一步:" -ForegroundColor Yellow
Write-Host "  1. 激活环境: venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  2. 运行测试: python test_detector.py" -ForegroundColor White
Write-Host "  3. 启动应用: python app\main.py" -ForegroundColor White
Write-Host ""

pause







