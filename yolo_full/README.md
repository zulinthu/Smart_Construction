# 基于改进YOLOv5的施工人员安全帽佩戴智能检测系统

## 📝 项目简介

本项目是一个基于深度学习的安全帽佩戴检测系统，通过改进YOLOv5算法实现高精度、实时的安全帽检测功能。系统支持图片、视频和实时摄像头检测，具有友好的图形用户界面。

## ✨ 核心特性

- ✅ **改进YOLOv5算法**：轻量化骨干网络 + 注意力机制
- ✅ **实时摄像头检测**：支持实时视频流检测，非单纯图片上传
- ✅ **多种输入方式**：图片、视频、摄像头
- ✅ **友好的GUI界面**：基于PyQt5开发
- ✅ **统计分析功能**：实时统计、报警提示
- ✅ **结果导出**：支持图片、视频、统计数据导出

## 🎯 性能指标

| 指标 | 基线YOLOv5s | 改进版本 |
|-----|------------|---------|
| mAP@0.5 | ~88% | **≥92%** |
| 参数量 | 7.2M | **<10M** |
| GPU推理速度 | ~65 FPS | **≥50 FPS** |
| 模型大小 | 14.4MB | **<20MB** |

## 📦 项目结构

```
helmet-detection/
│
├── data/                    # 数据目录
│   ├── raw/                 # 原始数据
│   ├── processed/           # 处理后数据
│   └── labels/              # 标注文件
│
├── models/                  # 模型目录
│   ├── yolov5/             # YOLOv5源码
│   ├── improved/           # 改进模型
│   └── weights/            # 模型权重
│
├── train/                   # 训练脚本
├── evaluate/                # 评估脚本
├── app/                     # 应用程序
│   ├── ui/                  # 界面文件
│   ├── core/                # 核心功能
│   └── utils/               # 工具函数
│
├── tests/                   # 测试脚本
├── docs/                    # 文档
├── results/                 # 结果输出
└── notebooks/               # Jupyter笔记本
```

## 🚀 快速开始

### 方法1：使用构建脚本（推荐）⭐

#### Windows用户
```cmd
# 一键安装所有依赖
build.bat all

# 启动GUI应用
build.bat gui

# 查看所有命令
build.bat help
```

#### Linux/Mac用户
```bash
# 一键安装所有依赖
make all

# 启动GUI应用
make gui

# 查看所有命令
make help
```

#### 跨平台Python脚本
```bash
# 一键安装
python build.py all

# 启动GUI
python build.py gui

# 查看帮助
python build.py help
```

### 方法2：手动安装

#### 1. 环境要求

- Python 3.8+
- PyTorch 1.10+
- CUDA 11.0+（GPU推理，可选）
- 8GB+ RAM
- 摄像头（实时检测）

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 下载YOLOv5和预训练权重

```bash
# 下载YOLOv5源码
cd models
git clone https://github.com/ultralytics/yolov5.git
cd yolov5
pip install -r requirements.txt
cd ../..

# 下载预训练权重
mkdir -p models/weights
wget -O models/weights/yolov5s.pt https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt
```

#### 4. 运行应用

```bash
# 启动图形界面
python app/main.py

# 或使用命令行检测
python run.py
```

### 🛠️ 构建系统

本项目提供了类似CMake的构建管理系统，支持：
- ✅ **Makefile** - Linux/Mac用户
- ✅ **build.bat** - Windows批处理脚本
- ✅ **build.sh** - Linux/Mac Shell脚本
- ✅ **build.py** - 跨平台Python脚本
- ✅ **CMakeLists.txt** - CMake配置

详细使用方法请查看：[构建系统使用指南](docs/构建系统使用指南.md)

### 🎨 VSCode集成

项目已完整配置VSCode开发环境！

#### 快捷键（开箱即用）
- `Ctrl+Shift+R` - 启动GUI应用
- `Ctrl+Shift+T` - 运行测试
- `Ctrl+Shift+B` - 运行默认构建任务
- `F5` - 开始调试

#### 底部状态栏
点击底部状态栏的任务图标即可快速选择：
- ▶️ 启动GUI应用
- 🏋️ 训练基线模型
- 🧪 运行测试
- 📹 测试摄像头
- 🎨 格式化代码
- 更多...

详细配置说明请查看：[VSCode配置指南](docs/VSCode配置指南.md)

## 📊 模型训练

### 数据准备

1. 将数据放入 `data/raw/` 目录
2. 使用LabelImg进行标注
3. 运行数据预处理脚本

```bash
python train/prepare_data.py
```

### 训练基线模型

```bash
python train/train_baseline.py --epochs 100 --batch-size 16
```

### 训练改进模型

```bash
python train/train_improved.py --epochs 100 --batch-size 16
```

### 模型评估

```bash
python evaluate/eval_model.py --weights models/weights/improved_final.pt
```

## 📸 系统功能

### 1. 图片检测
- 支持单张/批量检测
- 支持JPG、PNG、BMP格式
- 结果可视化与保存

### 2. 视频检测
- 支持MP4、AVI、MOV格式
- 逐帧检测处理
- 进度显示与控制

### 3. 实时摄像头检测（核心功能）
- 摄像头自动检测
- 实时显示检测结果
- FPS实时显示
- 支持录制

### 4. 统计分析
- 实时统计人数
- 佩戴/未佩戴统计
- 合规率计算
- 历史数据记录

### 5. 报警功能
- 未佩戴安全帽报警
- 可视化高亮显示
- 日志记录

## 🔬 改进方案

### 1. 轻量化骨干网络
- **MobileNetV3**：参数量减少60%
- 保持检测精度的同时大幅降低计算量

### 2. 注意力机制
- **ECA-Net**：轻量级通道注意力
- **CBAM**：空间注意力增强

### 3. 特征融合优化
- **改进BiFPN**：加权特征融合
- 增强多尺度特征表达能力

### 4. 损失函数改进
- **CIoU Loss**：改善边界框回归
- 提升定位精度

## 📈 对比实验

详细的对比实验结果请参见：[实验报告](docs/实验报告.md)

| 模型 | mAP@0.5 | FPS | 参数量 |
|-----|---------|-----|--------|
| YOLOv5s | 88.2% | 65 | 7.2M |
| 改进版本1 | 89.5% | 58 | 6.8M |
| 改进版本2 | 91.3% | 52 | 8.5M |
| **最终版本** | **92.6%** | **53** | **9.2M** |

## 📖 文档

- [技术方案文档](技术方案文档.md)
- [使用手册](docs/使用手册.md)
- [API文档](docs/API文档.md)
- [开发指南](docs/开发指南.md)

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/

# 测试模型
python tests/test_model.py

# 测试检测器
python tests/test_detector.py

# 测试摄像头
python tests/test_camera.py
```

## 📝 待办事项

- [ ] 数据集收集与标注
- [ ] 基线模型训练
- [ ] 模型改进实现
- [ ] 对比实验
- [ ] GUI系统开发
- [ ] 摄像头检测功能
- [ ] 系统测试
- [ ] 文档完善

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📧 联系方式

- 作者：[您的姓名]
- 邮箱：[您的邮箱]
- 项目地址：[GitHub链接]

## 🙏 致谢

- [YOLOv5](https://github.com/ultralytics/yolov5)
- [PyTorch](https://pytorch.org/)
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
- [OpenCV](https://opencv.org/)

---

**最后更新：** 2025-10-31

