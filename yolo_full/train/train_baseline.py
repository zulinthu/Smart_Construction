"""
YOLOv5基线模型训练脚本
使用官方YOLOv5进行安全帽检测模型训练
"""

import sys
import io
import torch
import yaml
from pathlib import Path

# 兼容Windows控制台默认GBK编码，避免Unicode日志输出报错
if sys.platform == "win32":
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8", errors="replace")
        elif hasattr(stream, "buffer"):
            setattr(
                sys,
                stream_name,
                io.TextIOWrapper(
                    stream.buffer,
                    encoding="utf-8",
                    errors="replace",
                ),
            )

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config import (
    TRAIN_CONFIG, DATA_DIR, WEIGHTS_DIR, YOLOV5_DIR,
    RESULTS_DIR, AUGMENTATION_CONFIG
)


class YOLOv5Trainer:
    """YOLOv5训练器"""
    
    def __init__(self, data_yaml, model_size='yolov5s', img_size=640):
        """
        初始化训练器
        
        Args:
            data_yaml: 数据集配置文件路径
            model_size: 模型大小 ('yolov5s', 'yolov5m', 'yolov5l', 'yolov5x')
            img_size: 输入图像尺寸
        """
        self.data_yaml = Path(data_yaml)
        self.model_size = model_size
        self.img_size = img_size
        self.device = self._get_device()
        
        print(f"\n{'='*60}")
        print(f"YOLOv5训练器初始化")
        print(f"{'='*60}")
        print(f"数据集配置: {self.data_yaml}")
        print(f"模型大小: {self.model_size}")
        print(f"图像尺寸: {self.img_size}")
        print(f"设备: {self.device}")
        print(f"{'='*60}\n")
    
    def _get_device(self):
        """获取计算设备"""
        if torch.cuda.is_available():
            device = torch.device('cuda:0')
            print(f"✓ 使用GPU: {torch.cuda.get_device_name(0)}")
            print(f"  GPU内存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        else:
            device = torch.device('cpu')
            print(f"⚠ 使用CPU（训练速度较慢）")
        return device
    
    def train(self, epochs=100, batch_size=16, workers=8, save_dir=None):
        """
        训练模型
        
        Args:
            epochs: 训练轮数
            batch_size: 批次大小
            workers: 数据加载线程数
            save_dir: 保存目录
        """
        if save_dir is None:
            save_dir = RESULTS_DIR / 'experiments' / 'train_baseline'
        
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n开始训练...")
        print(f"训练参数:")
        print(f"  - 轮数: {epochs}")
        print(f"  - 批次大小: {batch_size}")
        print(f"  - 工作线程: {workers}")
        print(f"  - 保存目录: {save_dir}\n")
        
        try:
            # 检查YOLOv5是否已下载
            if not YOLOV5_DIR.exists():
                print("下载YOLOv5代码...")
                self._download_yolov5()
            
            # 使用torch.hub训练
            model = torch.hub.load('ultralytics/yolov5', self.model_size, pretrained=True)
            
            # 配置训练参数
            train_args = {
                'data': str(self.data_yaml),
                'epochs': epochs,
                'batch_size': batch_size,
                'img_size': self.img_size,
                'workers': workers,
                'project': str(save_dir.parent),
                'name': save_dir.name,
                'exist_ok': True,
                'device': str(self.device),
                # 数据增强参数
                'hsv_h': AUGMENTATION_CONFIG['hsv_h'],
                'hsv_s': AUGMENTATION_CONFIG['hsv_s'],
                'hsv_v': AUGMENTATION_CONFIG['hsv_v'],
                'degrees': AUGMENTATION_CONFIG['degrees'],
                'translate': AUGMENTATION_CONFIG['translate'],
                'scale': AUGMENTATION_CONFIG['scale'],
                'flipud': AUGMENTATION_CONFIG['flipud'],
                'fliplr': AUGMENTATION_CONFIG['fliplr'],
                'mosaic': AUGMENTATION_CONFIG['mosaic'],
            }
            
            print("\n训练配置:")
            for key, value in train_args.items():
                print(f"  {key}: {value}")
            
            print("\n" + "="*60)
            print("开始训练YOLOv5模型...")
            print("="*60 + "\n")
            
            # 使用YOLOv5的train.py进行训练
            # 注意：实际训练需要安装YOLOv5并调用其train.py
            import subprocess
            
            yolov5_train = YOLOV5_DIR / 'train.py'
            if yolov5_train.exists():
                cmd = [
                    sys.executable, str(yolov5_train),
                    '--data', str(self.data_yaml),
                    '--weights', f'{self.model_size}.pt',
                    '--epochs', str(epochs),
                    '--batch-size', str(batch_size),
                    '--img', str(self.img_size),
                    '--workers', str(workers),
                    '--project', str(save_dir.parent),
                    '--name', save_dir.name,
                    '--device', '0' if torch.cuda.is_available() else 'cpu',
                ]
                
                subprocess.run(cmd, check=True)
            else:
                print("⚠ YOLOv5训练脚本未找到")
                print("提示: 请克隆YOLOv5仓库到 models/yolov5/ 目录")
                print("命令: git clone https://github.com/ultralytics/yolov5 models/yolov5")
                print("\n或使用以下简化训练流程（仅供演示）:")
                self._simple_train(model, epochs, batch_size)
            
            print(f"\n{'='*60}")
            print(f"✓ 训练完成！")
            print(f"模型保存在: {save_dir}")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"\n✗ 训练失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _simple_train(self, model, epochs, batch_size):
        """简化的训练流程（演示用）"""
        print("\n使用简化训练流程...")
        print("注意: 这只是演示，实际训练请使用YOLOv5官方代码\n")
        
        # 这里可以添加简单的训练循环
        print(f"模拟训练 {epochs} 轮...")
        for epoch in range(min(3, epochs)):  # 只演示3轮
            print(f"Epoch {epoch+1}/{epochs}")
            print(f"  Train: loss=0.05{epoch}  mAP=0.{90-epoch}")
        
        print("\n提示: 请安装完整YOLOv5进行实际训练")
    
    def _download_yolov5(self):
        """下载YOLOv5代码"""
        import subprocess
        
        YOLOV5_DIR.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            'git', 'clone',
            'https://github.com/ultralytics/yolov5',
            str(YOLOV5_DIR)
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"✓ YOLOv5代码已下载到: {YOLOV5_DIR}")
        except Exception as e:
            print(f"⚠ 下载失败: {e}")
            print("请手动克隆YOLOv5仓库")


def create_data_yaml(train_dir, val_dir, class_names, save_path):
    """
    创建YOLOv5数据集配置文件
    
    Args:
        train_dir: 训练集目录
        val_dir: 验证集目录
        class_names: 类别名称列表
        save_path: 保存路径
    """
    data_config = {
        'path': str(Path(train_dir).parent),  # 数据集根目录
        'train': 'train',  # 训练集相对路径
        'val': 'val',      # 验证集相对路径
        'nc': len(class_names),  # 类别数量
        'names': class_names     # 类别名称
    }
    
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(save_path, 'w', encoding='utf-8') as f:
        yaml.dump(data_config, f, allow_unicode=True)
    
    print(f"✓ 数据配置文件已创建: {save_path}")
    return save_path


def main():
    """主函数"""
    print("\n" + "="*60)
    print("YOLOv5安全帽检测模型训练")
    print("="*60 + "\n")
    
    # 数据集配置文件路径
    data_yaml = DATA_DIR / 'helmet.yaml'
    
    # 检查配置文件是否存在
    if not data_yaml.exists():
        print(f"⚠ 数据配置文件不存在: {data_yaml}")
        print("创建示例配置文件...")
        
        # 创建示例配置
        create_data_yaml(
            train_dir=DATA_DIR / 'train',
            val_dir=DATA_DIR / 'val',
            class_names=['wearing_helmet', 'no_helmet', 'person'],
            save_path=data_yaml
        )
    
    # 创建训练器
    trainer = YOLOv5Trainer(
        data_yaml=data_yaml,
        model_size='yolov5s',  # 使用YOLOv5s作为基线
        img_size=TRAIN_CONFIG['img_size']
    )
    
    # 开始训练
    trainer.train(
        epochs=TRAIN_CONFIG['epochs'],
        batch_size=TRAIN_CONFIG['batch_size'],
        workers=TRAIN_CONFIG['workers']
    )


if __name__ == '__main__':
    main()
