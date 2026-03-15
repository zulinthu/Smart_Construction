# 🔧 Python 3.11 环境配置指南

## 📥 第一步：安装 Python 3.11

### 下载
- 链接已在浏览器打开
- 或访问：https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

### 安装步骤
1. ✅ 运行下载的安装程序
2. ✅ **重要**：勾选 "Add Python 3.11 to PATH"
3. ✅ 选择 "Install Now"
4. ✅ 等待安装完成
5. ✅ 关闭安装程序

### 验证安装
安装完成后，**打开新的命令提示符**，运行：
```bash
python --version
```
应该显示：`Python 3.11.9`

---

## 🔄 第二步：自动配置环境（推荐）

**最简单的方法**：运行自动化脚本

```bash
# 在项目目录下运行
setup_env.bat
```

这个脚本会自动：
- ✓ 创建虚拟环境
- ✓ 安装所有依赖
- ✓ 验证安装

**运行完成后跳到第四步！**

---

## 🛠️ 第二步（手动）：创建虚拟环境

如果不想用自动脚本，手动执行：

```bash
# 1. 删除旧环境（如果存在）
rmdir /s /q venv

# 2. 创建新虚拟环境
python -m venv venv

# 3. 激活虚拟环境
venv\Scripts\activate.bat

# 提示符应该变成 (venv) D:\htools\order\1031\yolo>
```

---

## 📦 第三步（手动）：安装依赖

在**激活的虚拟环境**中运行：

```bash
# 升级 pip
python -m pip install --upgrade pip

# 安装 PyTorch (CPU版本，稳定)
pip install torch==2.2.0 torchvision==0.17.0 --index-url https://download.pytorch.org/whl/cpu

# 安装 GUI 框架
pip install PyQt5==5.15.10

# 安装 OpenCV
pip install opencv-python==4.10.0.84

# 安装数据处理
pip install numpy pandas

# 安装可视化
pip install matplotlib seaborn

# 安装 YOLOv5 相关
pip install ultralytics scipy tqdm tensorboard pyyaml
```

或者一次性安装：
```bash
pip install torch==2.2.0 torchvision==0.17.0 PyQt5==5.15.10 opencv-python==4.10.0.84 numpy pandas matplotlib seaborn ultralytics scipy tqdm tensorboard pyyaml --index-url https://download.pytorch.org/whl/cpu
```

---

## ✅ 第四步：验证安装

```bash
# 测试导入
python -c "import torch; import cv2; from PyQt5 import QtCore; print('✓ 所有依赖已安装')"

# 运行完整测试
python test_detector.py

# 启动应用
python app\main.py
```

---

## 📝 常见问题

### Q: 虚拟环境激活后，提示找不到 python？
**A**: 重新打开命令提示符，确保 Python 3.11 在 PATH 中

### Q: pip 安装很慢？
**A**: 使用国内镜像：
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple <包名>
```

### Q: 还是有 DLL 错误？
**A**: 安装 Visual C++ Redistributable：
https://aka.ms/vs/17/release/vc_redist.x64.exe

---

## 🎯 完整流程总结

```bash
# 1. 安装 Python 3.11 后，新开命令提示符

# 2. 进入项目目录
cd D:\htools\order\1031\yolo

# 3. 运行自动配置脚本
setup_env.bat

# 4. 等待完成后测试
python test_detector.py

# 5. 启动应用
python app\main.py
```

---

## 💡 虚拟环境使用

### 激活虚拟环境
```bash
venv\Scripts\activate.bat
```

### 退出虚拟环境
```bash
deactivate
```

### 以后每次使用
```bash
# 1. 激活环境
venv\Scripts\activate.bat

# 2. 运行应用
python app\main.py
```

---

**安装完 Python 3.11 后，直接运行 `setup_env.bat` 即可！**







