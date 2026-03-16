"""
项目配置文件
定义所有配置参数和路径
"""

import os
from pathlib import Path

# ==================== 项目路径配置 ====================
# 项目根目录
ROOT_DIR = Path(__file__).parent.absolute()

# 数据目录
DATA_DIR = ROOT_DIR / 'data'
DATA_RAW_DIR = DATA_DIR / 'raw'
DATA_PROCESSED_DIR = DATA_DIR / 'processed'
DATA_LABELS_DIR = DATA_DIR / 'labels'

# 模型目录
MODELS_DIR = ROOT_DIR / 'models'
YOLOV5_DIR = MODELS_DIR / 'yolov5'
IMPROVED_DIR = MODELS_DIR / 'improved'
WEIGHTS_DIR = MODELS_DIR / 'weights'

# 结果目录
RESULTS_DIR = ROOT_DIR / 'results'
RESULTS_IMAGES_DIR = RESULTS_DIR / 'images'
RESULTS_VIDEOS_DIR = RESULTS_DIR / 'videos'
RESULTS_LOGS_DIR = RESULTS_DIR / 'logs'
RESULTS_STATISTICS_DIR = RESULTS_DIR / 'statistics'

# ==================== 模型配置 ====================
# 模型类型
MODEL_TYPE = 'improved'  # 'baseline' or 'improved'

# 模型权重路径
BASELINE_WEIGHTS = WEIGHTS_DIR / 'yolov5s.pt'
IMPROVED_WEIGHTS = WEIGHTS_DIR / 'improved_final.pt'

# 输入图像尺寸
IMG_SIZE = 640

# 检测类别
CLASS_NAMES = ['wearing_helmet', 'no_helmet', 'person']
CLASS_COLORS = {
    'wearing_helmet': (0, 255, 0),      # 绿色
    'no_helmet': (0, 0, 255),           # 红色
    'person': (255, 0, 0)               # 蓝色
}

# 类别中文名称
CLASS_NAMES_ZH = {
    'wearing_helmet': 'Wearing Helmet',
    'no_helmet': 'No Helmet',
    'person': 'Person'
}

NUM_CLASSES = len(CLASS_NAMES)

# ==================== 检测配置 ====================
# 置信度阈值
CONF_THRESHOLD = 0.25

# NMS IoU阈值
IOU_THRESHOLD = 0.45

# 最大检测数
MAX_DETECTIONS = 1000

# 设备配置
DEVICE = 'cuda:0'  # 'cuda:0' 或 'cpu'

# 半精度推理
FP16 = True

# ==================== 训练配置 ====================
# 训练参数
TRAIN_CONFIG = {
    'epochs': 100,
    'batch_size': 16,
    'img_size': 640,
    'learning_rate': 0.001,
    'optimizer': 'Adam',
    'weight_decay': 0.0005,
    'momentum': 0.937,
    'warmup_epochs': 3,
    'workers': 8,
}

# 数据增强配置
AUGMENTATION_CONFIG = {
    'hsv_h': 0.015,      # HSV色调增强
    'hsv_s': 0.7,        # HSV饱和度增强
    'hsv_v': 0.4,        # HSV明度增强
    'degrees': 10.0,     # 旋转角度
    'translate': 0.1,    # 平移
    'scale': 0.5,        # 缩放
    'shear': 0.0,        # 剪切
    'perspective': 0.0,  # 透视
    'flipud': 0.0,       # 上下翻转
    'fliplr': 0.5,       # 左右翻转
    'mosaic': 1.0,       # Mosaic增强
    'mixup': 0.0,        # Mixup增强
}

# ==================== 摄像头配置 ====================
# 默认摄像头ID
CAMERA_ID = 0

# 摄像头分辨率
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# 摄像头FPS
CAMERA_FPS = 30

# 视频编码格式
VIDEO_CODEC = 'mp4v'

# ==================== 界面配置 ====================
# 窗口尺寸
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900

# 主题配置
THEME = 'default'  # 'default', 'dark', 'light'

# 字体配置
FONT_FAMILY = 'Microsoft YaHei'
FONT_SIZE = 10

# 显示FPS
SHOW_FPS = True

# 显示置信度
SHOW_CONFIDENCE = True

# 显示类别标签
SHOW_LABELS = True

# ==================== 报警配置 ====================
# 启用报警
ALARM_ENABLED = True

# 报警阈值（未佩戴安全帽的人数）
ALARM_THRESHOLD = 1

# 合规率阈值（低于此值报警）
COMPLIANCE_THRESHOLD = 80.0

# 声音报警
SOUND_ALARM = False

# ==================== 日志配置 ====================
# 日志级别
LOG_LEVEL = 'INFO'  # 'DEBUG', 'INFO', 'WARNING', 'ERROR'

# 日志文件路径
LOG_FILE = RESULTS_LOGS_DIR / 'system.log'

# 日志格式
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ==================== 性能配置 ====================
# 批处理大小（检测时）
DETECT_BATCH_SIZE = 1

# 多线程数量
NUM_THREADS = 4

# 内存优化
MEMORY_OPTIMIZATION = True

# ==================== 导出配置 ====================
# 图片导出格式
IMAGE_EXPORT_FORMAT = 'jpg'  # 'jpg', 'png'

# 图片导出质量
IMAGE_EXPORT_QUALITY = 95

# 视频导出格式
VIDEO_EXPORT_FORMAT = 'mp4'  # 'mp4', 'avi'

# 视频导出FPS
VIDEO_EXPORT_FPS = 30

# 统计数据导出格式
STATISTICS_EXPORT_FORMAT = 'csv'  # 'csv', 'excel'

# ==================== 功能开关 ====================
# 启用GPU加速
USE_GPU = True

# 启用TensorRT加速（需要安装TensorRT）
USE_TENSORRT = False

# 启用ONNX Runtime加速
USE_ONNX = False

# 启用多GPU训练
MULTI_GPU = False

# 启用混合精度训练
MIXED_PRECISION = True

# ==================== 其他配置 ====================
# 随机种子
RANDOM_SEED = 42

# 是否显示详细信息
VERBOSE = True

# 保存检测结果
SAVE_RESULTS = True

# 保存检测图片
SAVE_IMAGES = True

# 保存检测视频
SAVE_VIDEOS = False

# 保存统计数据
SAVE_STATISTICS = True


# ==================== 配置验证和初始化 ====================
def init_directories():
    """创建必要的目录"""
    dirs = [
        DATA_RAW_DIR, DATA_PROCESSED_DIR, DATA_LABELS_DIR,
        WEIGHTS_DIR, IMPROVED_DIR,
        RESULTS_IMAGES_DIR, RESULTS_VIDEOS_DIR,
        RESULTS_LOGS_DIR, RESULTS_STATISTICS_DIR
    ]

    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)

    print(f"✓ 项目目录初始化完成")


def get_device():
    """获取计算设备"""
    import torch

    if USE_GPU and torch.cuda.is_available():
        device = torch.device('cuda:0')
        print(f"✓ 使用GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device('cpu')
        print(f"✓ 使用CPU")

    return device


def print_config():
    """打印配置信息"""
    print("\n" + "="*60)
    print("系统配置信息")
    print("="*60)
    print(f"项目根目录: {ROOT_DIR}")
    print(f"模型类型: {MODEL_TYPE}")
    print(f"输入尺寸: {IMG_SIZE}")
    print(f"置信度阈值: {CONF_THRESHOLD}")
    print(f"IoU阈值: {IOU_THRESHOLD}")
    print(f"设备: {DEVICE}")
    print(f"半精度推理: {FP16}")
    print(f"摄像头ID: {CAMERA_ID}")
    print(f"报警启用: {ALARM_ENABLED}")
    print("="*60 + "\n")


if __name__ == '__main__':
    # 初始化目录
    init_directories()

    # 打印配置
    print_config()

    # 测试设备
    try:
        device = get_device()
    except ImportError:
        print("注意: PyTorch未安装，请运行 pip install torch")


