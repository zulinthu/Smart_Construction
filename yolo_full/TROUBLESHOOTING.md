# 🔧 故障排除指南

## ❌ 常见问题及解决方案

### 1. 模型下载失败

#### 问题描述
```
✗ 模型加载失败: 'Authorization'
HTTP Error 403: rate limit exceeded
```

#### 原因
- GitHub API 访问限制
- 网络连接问题
- 防火墙阻止

#### 解决方案

**方案A: 使用下载工具（推荐）**
```bash
python download_models.py yolov5s
```

**方案B: 手动下载**
1. 打开浏览器访问: https://github.com/ultralytics/yolov5/releases/tag/v7.0
2. 下载 `yolov5s.pt` 文件（14.4 MB）
3. 创建目录 `models/weights/`
4. 将文件放到该目录

**方案C: 使用直接链接**
```bash
# Windows PowerShell
Invoke-WebRequest -Uri "https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt" -OutFile "models/weights/yolov5s.pt"

# Linux/Mac
wget https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt -P models/weights/

# 或使用 curl
curl -L https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt -o models/weights/yolov5s.pt
```

**方案D: 使用国内镜像**
```bash
# 百度网盘等国内云盘下载后放到 models/weights/
```

#### 验证
```python
from pathlib import Path
model_path = Path('models/weights/yolov5s.pt')
print(f"模型存在: {model_path.exists()}")
print(f"文件大小: {model_path.stat().st_size / 1024 / 1024:.2f} MB")
```

---

### 2. PyQt5 安装失败

#### 问题描述
```
ModuleNotFoundError: No module named 'PyQt5'
```

#### 解决方案
```bash
# 方法1: 使用 pip
pip install PyQt5

# 方法2: 使用清华镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple PyQt5

# 方法3: 使用 conda
conda install pyqt

# Windows 可能需要安装 Visual C++ 运行时
# 下载: https://aka.ms/vs/17/release/vc_redist.x64.exe
```

---

### 3. CUDA 不可用

#### 问题描述
```
⚠ CUDA不可用，使用CPU
```

#### 检查
```python
import torch
print(f"CUDA 可用: {torch.cuda.is_available()}")
print(f"CUDA 版本: {torch.version.cuda}")
print(f"设备数量: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"设备名称: {torch.cuda.get_device_name(0)}")
```

#### 解决方案

**如果确实有GPU:**
1. 安装对应CUDA版本的PyTorch
```bash
# CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

2. 更新NVIDIA驱动
- 访问: https://www.nvidia.com/Download/index.aspx
- 下载最新驱动

**如果没有GPU:**
- 使用CPU版本（已自动适配）
- 性能会慢一些，但功能完整

---

### 4. 中文显示乱码

#### Windows 控制台
```bash
# PowerShell
$env:PYTHONIOENCODING="utf-8"
python app/main.py

# CMD
chcp 65001
python app/main.py
```

#### 代码中已处理
程序启动时自动设置UTF-8编码。

---

### 5. 内存不足

#### 问题描述
```
RuntimeError: CUDA out of memory
或程序崩溃
```

#### 解决方案
1. 减小图像尺寸
```python
detector = HelmetDetector(img_size=320)  # 默认640
```

2. 使用更小的模型
```bash
python download_models.py yolov5n  # 3.9 MB
```

3. 使用CPU
```python
detector = HelmetDetector(device='cpu')
```

---

### 6. OpenCV 导入错误

#### 问题描述
```
ImportError: DLL load failed while importing cv2
```

#### 解决方案
```bash
# 卸载旧版本
pip uninstall opencv-python opencv-contrib-python

# 重新安装
pip install opencv-python

# 如果还是失败，尝试
pip install opencv-python-headless
```

---

### 7. 检测速度慢

#### 优化建议

1. **使用GPU**
```python
detector = HelmetDetector(device='cuda:0')
```

2. **降低图像尺寸**
```python
detector = HelmetDetector(img_size=416)  # 更快但精度略低
```

3. **使用更小的模型**
- yolov5n: 最快（3.9MB）
- yolov5s: 平衡（14.4MB）

4. **批量处理**
- 视频检测时不显示窗口
- 使用多进程处理多个文件

---

### 8. GUI 无法启动

#### 检查依赖
```bash
python -c "from PyQt5 import QtCore; print(QtCore.QT_VERSION_STR)"
```

#### Windows 可能需要
```bash
# 安装 Visual C++ 运行时
# https://aka.ms/vs/17/release/vc_redist.x64.exe
```

#### Linux 可能需要
```bash
sudo apt-get install python3-pyqt5
sudo apt-get install libxcb-xinerama0
```

---

### 9. 模型加载超时

#### 增加超时时间
```python
import socket
socket.setdefaulttimeout(300)  # 5分钟

from app.core.detector import HelmetDetector
detector = HelmetDetector()
```

---

### 10. 权限错误

#### Windows
```bash
# 以管理员身份运行 PowerShell
```

#### Linux/Mac
```bash
sudo chown -R $USER:$USER models/
chmod -R 755 models/
```

---

## 📞 获取帮助

### 日志收集
运行时添加详细日志：
```bash
python app/main.py --verbose 2>&1 | tee error.log
```

### 提交Issue
包含以下信息：
1. 操作系统版本
2. Python版本
3. 依赖版本
```bash
python --version
pip list | grep -E "torch|opencv|PyQt5"
```
4. 完整错误日志
5. 复现步骤

### 联系方式
- GitHub Issues: https://github.com/zulinthu/yolo/issues
- 文档: docs/ 目录

---

## 🎯 快速诊断脚本

创建 `diagnose.py`:
```python
import sys
import subprocess

print("="*60)
print("系统诊断")
print("="*60)

# Python 版本
print(f"Python: {sys.version}")

# 检查依赖
packages = ['torch', 'torchvision', 'cv2', 'PyQt5', 'numpy', 'pandas']
for pkg in packages:
    try:
        if pkg == 'cv2':
            import cv2
            print(f"✓ opencv-python: {cv2.__version__}")
        elif pkg == 'PyQt5':
            from PyQt5 import QtCore
            print(f"✓ PyQt5: {QtCore.QT_VERSION_STR}")
        else:
            mod = __import__(pkg)
            print(f"✓ {pkg}: {mod.__version__}")
    except ImportError as e:
        print(f"✗ {pkg}: 未安装")

# CUDA
try:
    import torch
    print(f"\nCUDA可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
except:
    pass

print("="*60)
```

运行:
```bash
python diagnose.py
```

---

**最后更新**: 2024年11月
**版本**: v1.0







