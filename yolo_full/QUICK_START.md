# 🚀 快速开始指南

## 📦 环境准备

### 1. 安装依赖

```bash
# 基础依赖
pip install torch torchvision
pip install PyQt5
pip install opencv-python
pip install numpy pandas matplotlib seaborn
pip install tqdm pyyaml

# 或直接安装所有依赖
pip install -r requirements.txt
```

### 2. 验证安装

```bash
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "from PyQt5 import QtCore; print('PyQt5:', QtCore.QT_VERSION_STR)"
```

## 📥 下载模型（重要！）

首次使用需要下载YOLOv5模型权重：

### 方法1：使用下载工具（推荐）

```bash
# 下载YOLOv5s模型（推荐，14MB）
python download_models.py

# 或指定其他模型
python download_models.py yolov5n  # 最小模型，3.9MB
python download_models.py yolov5m  # 中等模型，40.8MB
```

### 方法2：手动下载

1. 访问：https://github.com/ultralytics/yolov5/releases/tag/v7.0
2. 下载 `yolov5s.pt`（推荐）
3. 放到 `models/weights/` 目录

### 方法3：自动下载（需要良好网络）

首次运行时会自动下载，但可能因网络问题失败。

## 🎯 快速运行

### 方法1：启动GUI应用

```bash
# Windows
python app/main.py

# Linux/Mac
python3 app/main.py
```

### 方法2：命令行检测

```python
from app.core.detector import HelmetDetector

# 创建检测器
detector = HelmetDetector(device='cpu')  # 或'cuda:0'

# 检测图片
annotated_img, detections, stats = detector.detect_image('test.jpg')

# 显示结果
import cv2
cv2.imshow('Result', annotated_img)
cv2.waitKey(0)
```

## 📸 使用GUI应用

### 1. 图片检测

1. 选择"图片检测"
2. 点击"选择文件"，选择图片
3. 点击"开始检测"
4. 查看检测结果和统计信息
5. 可选：保存标注结果

### 2. 视频检测

1. 选择"视频检测"
2. 点击"选择文件"，选择视频
3. 点击"开始检测"
4. 实时查看检测过程
5. 可选：保存检测结果视频

### 3. 摄像头检测

1. 选择"摄像头检测"
2. 选择摄像头ID（默认0）
3. 点击"开始检测"
4. 实时检测摄像头画面
5. 点击"停止"结束检测

## 🎨 参数调整

### 置信度阈值
- **用途**：过滤低置信度检测
- **范围**：0.01 - 0.99
- **推荐值**：0.25 - 0.50
- **说明**：值越高，误检越少但可能漏检

### IoU阈值
- **用途**：NMS（非极大值抑制）阈值
- **范围**：0.01 - 0.99
- **推荐值**：0.45 - 0.65
- **说明**：控制重叠框的合并程度

### 模型选择
- **YOLOv5s (基线)**：速度快，精度中等
- **改进版本**：精度高，速度略慢

## 📊 评估模型

```bash
# 评估图像集
python evaluate/eval_model.py

# 在代码中使用
from evaluate.eval_model import ModelEvaluator

evaluator = ModelEvaluator(weights_path='path/to/weights.pt', device='cpu')
metrics = evaluator.evaluate_images('test_images/')
```

## 🏋️ 训练模型

### 准备数据

1. 数据格式：YOLO格式
2. 目录结构：
```
data/
├── train/
│   ├── images/
│   └── labels/
└── val/
    ├── images/
    └── labels/
```

### 开始训练

```bash
# 使用训练脚本
python train/train_baseline.py

# 或在代码中
from train.train_baseline import YOLOv5Trainer

trainer = YOLOv5Trainer(
    data_yaml='data/helmet.yaml',
    model_size='yolov5s'
)

trainer.train(epochs=100, batch_size=16)
```

## 🔧 常见问题

### 1. GPU不可用

```python
# 检查CUDA
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))

# 使用CPU
detector = HelmetDetector(device='cpu')
```

### 2. 中文显示乱码

已在代码中处理Windows控制台UTF-8编码，如仍有问题：
```bash
# Windows PowerShell
$env:PYTHONIOENCODING="utf-8"
python app/main.py
```

### 3. 首次运行慢或失败

**问题**: 自动下载模型失败或很慢

**解决**:
```bash
# 使用下载工具
python download_models.py yolov5s

# 或手动下载模型
# 1. 访问: https://github.com/ultralytics/yolov5/releases
# 2. 下载 yolov5s.pt
# 3. 放到 models/weights/ 目录

# 然后在代码中指定路径
detector = HelmetDetector(weights_path='models/weights/yolov5s.pt')
```

### 4. 内存不足

- 减小batch_size
- 使用更小的模型（yolov5n/yolov5s）
- 降低图像尺寸（如640→320）

## 📁 项目结构

```
yolo/
├── app/               # 应用程序
│   ├── core/         # 核心检测器
│   ├── ui/           # GUI界面
│   └── utils/        # 工具函数
├── train/            # 训练脚本
├── evaluate/         # 评估脚本
├── models/           # 模型目录
├── data/             # 数据目录
├── results/          # 结果目录
└── docs/             # 文档
```

## 🎯 下一步

1. **准备数据集**：收集和标注安全帽图像
2. **训练模型**：使用自己的数据训练
3. **评估优化**：评估性能并优化参数
4. **部署应用**：打包成可执行文件

## 💡 提示

- **GPU加速**：使用CUDA可提速10-50倍
- **批量处理**：处理大量图片时建议使用批处理
- **模型优化**：可转换为ONNX格式以提高推理速度
- **数据增强**：训练时使用数据增强提高泛化能力

## 📞 获取帮助

- 查看文档：`docs/` 目录
- 查看示例：`notebooks/` 目录
- 提交Issue：GitHub Issues

---

**项目**: 安全帽检测系统
**框架**: YOLOv5 + PyQt5
**版本**: v1.0
**许可**: MIT

