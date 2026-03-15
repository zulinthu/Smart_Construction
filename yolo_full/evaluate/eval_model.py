"""
模型评估脚本
评估安全帽检测模型的性能指标
"""

import sys
import io
import torch
import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
    IMG_SIZE, CONF_THRESHOLD, IOU_THRESHOLD,
    CLASS_NAMES, RESULTS_DIR
)
from app.core.detector import HelmetDetector


class ModelEvaluator:
    """模型评估器"""
    
    def __init__(self, weights_path, device='cuda:0'):
        """
        初始化评估器
        
        Args:
            weights_path: 模型权重路径
            device: 计算设备
        """
        self.weights_path = Path(weights_path) if weights_path else None
        self.device = device
        
        print(f"\n{'='*60}")
        print("模型评估器初始化")
        print(f"{'='*60}")
        print(f"权重路径: {self.weights_path}")
        print(f"设备: {self.device}")
        print(f"{'='*60}\n")
        
        # 加载检测器
        self.detector = HelmetDetector(
            weights_path=str(self.weights_path) if self.weights_path else None,
            device=self.device,
            img_size=IMG_SIZE
        )
    
    def evaluate_images(self, image_dir, gt_dir=None, save_dir=None):
        """
        评估图像集
        
        Args:
            image_dir: 图像目录
            gt_dir: 真值标注目录（YOLO格式）
            save_dir: 结果保存目录
            
        Returns:
            metrics: 评估指标字典
        """
        image_dir = Path(image_dir)
        if save_dir is None:
            save_dir = RESULTS_DIR / 'evaluation'
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n开始评估图像集...")
        print(f"图像目录: {image_dir}")
        print(f"保存目录: {save_dir}\n")
        
        # 获取所有图像
        image_files = list(image_dir.glob('*.jpg')) + list(image_dir.glob('*.png'))
        
        if not image_files:
            print(f"⚠ 未找到图像文件: {image_dir}")
            return None
        
        print(f"找到 {len(image_files)} 张图像\n")
        
        # 统计信息
        total_stats = {
            'total_images': len(image_files),
            'total_detections': 0,
            'wearing_helmet': 0,
            'no_helmet': 0,
            'person': 0,
            'avg_confidence': 0.0,
            'avg_compliance_rate': 0.0,
        }
        
        all_confidences = []
        all_compliance_rates = []
        
        # 逐张处理
        for img_path in tqdm(image_files, desc="处理图像"):
            try:
                # 检测
                annotated_img, detections, statistics = self.detector.detect_image(str(img_path))
                
                # 更新统计
                total_stats['total_detections'] += len(detections)
                total_stats['wearing_helmet'] += statistics['wearing_helmet']
                total_stats['no_helmet'] += statistics['no_helmet']
                total_stats['person'] += statistics.get('person', 0)
                
                # 收集置信度和合规率
                if detections:
                    confidences = [d['confidence'] for d in detections]
                    all_confidences.extend(confidences)
                
                if statistics['total'] > 0:
                    all_compliance_rates.append(statistics['compliance_rate'])
                
                # 保存标注图像
                output_path = save_dir / 'images' / img_path.name
                output_path.parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(output_path), annotated_img)
                
            except Exception as e:
                print(f"⚠ 处理失败 {img_path.name}: {e}")
                continue
        
        # 计算平均值
        if all_confidences:
            total_stats['avg_confidence'] = np.mean(all_confidences)
        
        if all_compliance_rates:
            total_stats['avg_compliance_rate'] = np.mean(all_compliance_rates)
        
        # 打印结果
        print(f"\n{'='*60}")
        print("评估结果")
        print(f"{'='*60}")
        print(f"总图像数: {total_stats['total_images']}")
        print(f"总检测数: {total_stats['total_detections']}")
        print(f"佩戴安全帽: {total_stats['wearing_helmet']}")
        print(f"未佩戴安全帽: {total_stats['no_helmet']}")
        print(f"人员: {total_stats['person']}")
        print(f"平均置信度: {total_stats['avg_confidence']:.3f}")
        print(f"平均合规率: {total_stats['avg_compliance_rate']:.1f}%")
        print(f"{'='*60}\n")
        
        # 保存统计结果
        self._save_statistics(total_stats, all_confidences, all_compliance_rates, save_dir)
        
        return total_stats
    
    def _save_statistics(self, stats, confidences, compliance_rates, save_dir):
        """保存统计结果"""
        # 保存CSV
        stats_df = pd.DataFrame([stats])
        stats_csv = save_dir / 'statistics.csv'
        stats_df.to_csv(stats_csv, index=False)
        print(f"✓ 统计数据已保存: {stats_csv}")
        
        # 绘制图表
        self._plot_statistics(confidences, compliance_rates, save_dir)
    
    def _plot_statistics(self, confidences, compliance_rates, save_dir):
        """绘制统计图表"""
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # 置信度分布
        if confidences:
            axes[0].hist(confidences, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
            axes[0].axvline(np.mean(confidences), color='red', linestyle='--', 
                          label=f'平均值: {np.mean(confidences):.3f}')
            axes[0].set_xlabel('置信度')
            axes[0].set_ylabel('频数')
            axes[0].set_title('检测置信度分布')
            axes[0].legend()
            axes[0].grid(alpha=0.3)
        
        # 合规率分布
        if compliance_rates:
            axes[1].hist(compliance_rates, bins=20, color='lightgreen', edgecolor='black', alpha=0.7)
            axes[1].axvline(np.mean(compliance_rates), color='red', linestyle='--',
                          label=f'平均值: {np.mean(compliance_rates):.1f}%')
            axes[1].set_xlabel('合规率 (%)')
            axes[1].set_ylabel('频数')
            axes[1].set_title('安全帽佩戴合规率分布')
            axes[1].legend()
            axes[1].grid(alpha=0.3)
        
        plt.tight_layout()
        plot_path = save_dir / 'statistics_plot.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ 统计图表已保存: {plot_path}")
    
    def evaluate_video(self, video_path, save_dir=None, show=False):
        """
        评估视频
        
        Args:
            video_path: 视频路径
            save_dir: 保存目录
            show: 是否显示
            
        Returns:
            metrics: 评估指标
        """
        video_path = Path(video_path)
        if save_dir is None:
            save_dir = RESULTS_DIR / 'evaluation' / 'video'
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n开始评估视频...")
        print(f"视频路径: {video_path}")
        print(f"保存目录: {save_dir}\n")
        
        # 输出视频路径
        output_video = save_dir / f"{video_path.stem}_annotated.mp4"
        
        # 统计信息
        frame_stats = []
        all_fps = []
        
        # 处理视频
        for frame, annotated_frame, detections, statistics, fps in self.detector.detect_video(
            str(video_path), output_path=str(output_video), show=show
        ):
            frame_stats.append(statistics)
            all_fps.append(fps)
        
        # 计算平均统计
        avg_stats = {
            'total_frames': len(frame_stats),
            'avg_detections': np.mean([s['total'] for s in frame_stats]) if frame_stats else 0,
            'avg_wearing': np.mean([s['wearing_helmet'] for s in frame_stats]) if frame_stats else 0,
            'avg_no_helmet': np.mean([s['no_helmet'] for s in frame_stats]) if frame_stats else 0,
            'avg_compliance_rate': np.mean([s['compliance_rate'] for s in frame_stats]) if frame_stats else 0,
            'avg_fps': np.mean(all_fps) if all_fps else 0,
        }
        
        print(f"\n{'='*60}")
        print("视频评估结果")
        print(f"{'='*60}")
        print(f"总帧数: {avg_stats['total_frames']}")
        print(f"平均检测数: {avg_stats['avg_detections']:.2f}")
        print(f"平均佩戴: {avg_stats['avg_wearing']:.2f}")
        print(f"平均未佩戴: {avg_stats['avg_no_helmet']:.2f}")
        print(f"平均合规率: {avg_stats['avg_compliance_rate']:.1f}%")
        print(f"平均FPS: {avg_stats['avg_fps']:.1f}")
        print(f"输出视频: {output_video}")
        print(f"{'='*60}\n")
        
        # 保存统计
        stats_csv = save_dir / 'video_statistics.csv'
        pd.DataFrame([avg_stats]).to_csv(stats_csv, index=False)
        print(f"✓ 统计数据已保存: {stats_csv}")
        
        return avg_stats
    
    def compare_models(self, model_paths, test_dir, save_dir=None):
        """
        比较多个模型
        
        Args:
            model_paths: 模型路径列表
            test_dir: 测试图像目录
            save_dir: 保存目录
            
        Returns:
            comparison: 比较结果
        """
        if save_dir is None:
            save_dir = RESULTS_DIR / 'comparison'
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*60}")
        print("模型对比评估")
        print(f"{'='*60}\n")
        
        results = []
        
        for model_path in model_paths:
            model_name = Path(model_path).stem
            print(f"\n评估模型: {model_name}")
            
            # 创建评估器
            evaluator = ModelEvaluator(model_path, self.device)
            
            # 评估
            metrics = evaluator.evaluate_images(test_dir, save_dir=save_dir / model_name)
            
            if metrics:
                metrics['model'] = model_name
                results.append(metrics)
        
        # 保存比较结果
        if results:
            comparison_df = pd.DataFrame(results)
            comparison_csv = save_dir / 'model_comparison.csv'
            comparison_df.to_csv(comparison_csv, index=False)
            
            print(f"\n✓ 比较结果已保存: {comparison_csv}")
            print(f"\n对比表格:")
            print(comparison_df.to_string())
        
        return results


def main():
    """主函数"""
    print("\n" + "="*60)
    print("安全帽检测模型评估")
    print("="*60 + "\n")
    
    # 示例：评估预训练模型
    evaluator = ModelEvaluator(
        weights_path=None,  # 使用默认YOLOv5s
        device='cpu'
    )
    
    # 测试图像目录（请根据实际情况修改）
    test_dir = RESULTS_DIR / 'test_images'
    
    if test_dir.exists() and list(test_dir.glob('*.jpg')):
        # 评估图像
        metrics = evaluator.evaluate_images(test_dir)
    else:
        print(f"⚠ 测试目录不存在或为空: {test_dir}")
        print("提示: 请将测试图像放入该目录")
        print("\n或使用命令行指定测试目录:")
        print(f"python {__file__} --test-dir /path/to/test/images")


if __name__ == '__main__':
    main()
