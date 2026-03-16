"""
YOLOv5 安全帽检测器
实现图片、视频、摄像头的实时检测
"""

import cv2
import numpy as np
import torch
from pathlib import Path
import sys
import io
import importlib
from typing import Any, cast

try:
    from PIL import Image, ImageDraw, ImageFont
    _PIL_AVAILABLE = True
except Exception:  # pragma: no cover
    Image = None
    ImageDraw = None
    ImageFont = None
    _PIL_AVAILABLE = False

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
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

config = importlib.import_module("config")
CONF_THRESHOLD = config.CONF_THRESHOLD
IOU_THRESHOLD = config.IOU_THRESHOLD
CLASS_COLORS = config.CLASS_COLORS
CLASS_NAMES_ZH = config.CLASS_NAMES_ZH


class HelmetDetector:
    """安全帽检测器类"""

    def __init__(self, weights_path=None, device="cuda:0", img_size=640):
        """
        初始化检测器

        Args:
            weights_path: 模型权重路径
            device: 计算设备 ('cuda:0' 或 'cpu')
            img_size: 输入图像尺寸
        """
        self.device = self._get_device(device)
        self.img_size = img_size
        self.conf_threshold = CONF_THRESHOLD
        self.iou_threshold = IOU_THRESHOLD
        self._label_font = self._load_label_font(20)

        # 加载模型
        self.model: Any = self._load_model(weights_path)

        print("✓ 检测器初始化完成")
        print(f"  - 设备: {self.device}")
        print(f"  - 图像尺寸: {self.img_size}")
        print(f"  - 置信度阈值: {self.conf_threshold}")
        print(f"  - IoU阈值: {self.iou_threshold}")


    @staticmethod
    def _contains_non_ascii(text: str) -> bool:
        return any(ord(ch) > 127 for ch in str(text))

    @staticmethod
    def _load_label_font(size: int):
        if not _PIL_AVAILABLE:
            return None

        candidates = [
            Path("C:/Windows/Fonts/msyh.ttc"),
            Path("C:/Windows/Fonts/msyhbd.ttc"),
            Path("C:/Windows/Fonts/simhei.ttf"),
            Path("C:/Windows/Fonts/simsun.ttc"),
            Path("C:/Windows/Fonts/simkai.ttf"),
            Path("C:/Windows/Fonts/Deng.ttf"),
        ]
        for font_path in candidates:
            if font_path.exists():
                try:
                    return ImageFont.truetype(str(font_path), size=size)
                except Exception:
                    continue

        return None

    @staticmethod
    def _ascii_fallback_label(label: str) -> str:
        return (
            str(label)
            .replace("\u672a\u4f69\u6234\u5b89\u5168\u5e3d", "no_helmet")
            .replace("\u4f69\u6234\u5b89\u5168\u5e3d", "wearing_helmet")
            .replace("\u4eba\u5458", "person")
        )

    def _draw_label(self, image, bbox, label, color):
        x1, y1 = int(bbox[0]), int(bbox[1])

        if self._contains_non_ascii(label) and (not _PIL_AVAILABLE or self._label_font is None):
            label = self._ascii_fallback_label(label)

        if self._contains_non_ascii(label) and _PIL_AVAILABLE and self._label_font is not None:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(image_rgb)
            draw = ImageDraw.Draw(pil_img)
            if hasattr(draw, "textbbox"):
                l, t, r, b = draw.textbbox((0, 0), label, font=self._label_font)
                label_w, label_h = r - l, b - t
            else:
                label_w, label_h = draw.textsize(label, font=self._label_font)

            bg_x1 = max(0, x1)
            bg_y1 = max(0, y1 - label_h - 10)
            bg_x2 = bg_x1 + label_w + 6
            bg_y2 = bg_y1 + label_h + 6
            draw.rectangle((bg_x1, bg_y1, bg_x2, bg_y2), fill=(int(color[2]), int(color[1]), int(color[0])))
            draw.text((bg_x1 + 3, bg_y1 + 3), label, font=self._label_font, fill=(255, 255, 255))
            return cv2.cvtColor(np.asarray(pil_img), cv2.COLOR_RGB2BGR)

        (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(
            image,
            (x1, max(0, y1 - label_h - 10)),
            (x1 + label_w, y1),
            color,
            -1,
        )
        cv2.putText(
            image,
            label,
            (x1, max(0, y1 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
        )
        return image

    def _get_device(self, device):
        """Get compute device (GPU-only)."""
        device = str(device).strip()
        if not device.startswith("cuda"):
            raise RuntimeError(
                f"GPU-only mode is enabled. Invalid device='{device}'. "
                "Use a CUDA device like 'cuda:0'."
            )
        if not torch.cuda.is_available():
            raise RuntimeError(
                "GPU-only mode is enabled, but CUDA is not available.\n"
                "Check NVIDIA driver / CUDA runtime / PyTorch CUDA build.\n"
                "Quick checks:\n"
                "  nvidia-smi\n"
                "  python -c \"import torch; print(torch.cuda.is_available(), torch.version.cuda)\""
            )
        return torch.device(device)

    def _load_model(self, weights_path):
        """加载YOLOv5模型"""
        try:
            # 尝试加载torch.hub的YOLOv5模型
            if weights_path and Path(weights_path).exists():
                # 从本地权重加载
                model = cast(
                    Any,
                    torch.hub.load(
                        "ultralytics/yolov5",
                        "custom",
                        path=weights_path,
                        force_reload=False,
                        trust_repo=True,
                        skip_validation=True,
                    ),
                )
                print(f"✓ 从本地加载模型: {weights_path}")
            else:
                # 加载预训练模型
                print("正在加载YOLOv5模型...")
                print("提示: 首次运行会自动下载模型（约14MB），可能需要几分钟")

                model = cast(
                    Any,
                    torch.hub.load(
                        "ultralytics/yolov5",
                        "yolov5s",
                        pretrained=True,
                        force_reload=False,
                        trust_repo=True,
                        skip_validation=True,
                        verbose=False,
                    ),
                )
                print("✓ 加载YOLOv5s预训练模型成功")

            # 设置模型参数
            model.to(self.device)
            model.conf = self.conf_threshold
            model.iou = self.iou_threshold
            model.classes = None  # 检测所有类别
            model.max_det = 1000  # 最大检测数

            # 设置为评估模式
            model.eval()

            return model

        except Exception as e:
            print(f"\n✗ 模型加载失败: {e}")
            print("\n" + "=" * 60)
            print("解决方案:")
            print("=" * 60)
            print("方法1: 手动下载YOLOv5模型")
            print("  1. 访问: https://github.com/ultralytics/yolov5/releases")
            print("  2. 下载 yolov5s.pt")
            print("  3. 放到 models/weights/ 目录")
            print("  4. 使用: HelmetDetector(weights_path='models/weights/yolov5s.pt')")
            print()
            print("方法2: 克隆YOLOv5仓库到本地")
            print("  git clone https://github.com/ultralytics/yolov5")
            print("  cd yolov5")
            print("  pip install -r requirements.txt")
            print()
            print("方法3: 使用国内镜像")
            print("  pip install -i https://pypi.tuna.tsinghua.edu.cn/simple yolov5")
            print("=" * 60)
            raise

    def detect_image(self, image_path):
        """
        检测单张图片

        Args:
            image_path: 图片路径

        Returns:
            annotated_image: 标注后的图片
            detections: 检测结果列表
            statistics: 统计信息
        """
        # 读取图片
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"无法读取图片: {image_path}")

        # 执行检测
        return self._detect(image)

    def detect_video(self, video_path, output_path=None, show=True):
        """
        检测视频

        Args:
            video_path: 视频路径
            output_path: 输出视频路径（可选）
            show: 是否显示检测过程

        Yields:
            frame: 当前帧
            annotated_frame: 标注后的帧
            detections: 检测结果
            statistics: 统计信息
            fps: 当前FPS
        """
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            raise ValueError(f"无法打开视频: {video_path}")

        # 获取视频属性
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"✓ 视频信息: {width}x{height}, {fps}FPS, {total_frames}帧")

        # 创建视频写入器
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

        frame_count = 0
        import time

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # 记录时间用于计算FPS
                start_time = time.time()

                # 检测当前帧
                annotated_frame, detections, statistics = self._detect(frame)

                # 计算FPS
                processing_time = time.time() - start_time
                current_fps = 1.0 / processing_time if processing_time > 0 else 0

                # 在帧上显示FPS
                cv2.putText(
                    annotated_frame,
                    f"FPS: {current_fps:.1f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )

                # 写入输出视频
                if writer:
                    writer.write(annotated_frame)

                frame_count += 1

                yield frame, annotated_frame, detections, statistics, current_fps

        finally:
            cap.release()
            if writer:
                writer.release()
            print(f"✓ 处理完成: {frame_count}帧")

    def detect_camera(self, camera_id=0):
        """
        检测摄像头实时视频流

        Args:
            camera_id: 摄像头ID

        Yields:
            frame: 当前帧
            annotated_frame: 标注后的帧
            detections: 检测结果
            statistics: 统计信息
            fps: 当前FPS
        """
        cap = cv2.VideoCapture(camera_id)

        if not cap.isOpened():
            raise ValueError(f"无法打开摄像头: {camera_id}")

        print(f"✓ 摄像头已打开: {camera_id}")

        import time

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("⚠ 无法读取摄像头帧")
                    break

                # 记录时间
                start_time = time.time()

                # 检测
                annotated_frame, detections, statistics = self._detect(frame)

                # 计算FPS
                processing_time = time.time() - start_time
                current_fps = 1.0 / processing_time if processing_time > 0 else 0

                # 显示FPS
                cv2.putText(
                    annotated_frame,
                    f"FPS: {current_fps:.1f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )

                yield frame, annotated_frame, detections, statistics, current_fps

        finally:
            cap.release()
            print("✓ 摄像头已关闭")

    def _detect(self, image):
        """
        核心检测方法

        Args:
            image: OpenCV图像(BGR格式)

        Returns:
            annotated_image: 标注后的图像
            detections: 检测结果列表
            statistics: 统计信息字典
        """
        # 转换为RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # YOLOv5推理
        results = self.model(image_rgb, size=self.img_size)

        # 解析结果
        detections = []
        predictions = results.pandas().xyxy[0]  # 获取pandas格式的结果

        for _, row in predictions.iterrows():
            detection = {
                "class": row["name"],
                "confidence": float(row["confidence"]),
                "bbox": [
                    int(row["xmin"]),
                    int(row["ymin"]),
                    int(row["xmax"]),
                    int(row["ymax"]),
                ],
            }
            detections.append(detection)

        # 统计信息
        statistics = self._calculate_statistics(detections)

        # 绘制标注
        annotated_image = self._draw_annotations(image.copy(), detections, statistics)

        return annotated_image, detections, statistics

    def _calculate_statistics(self, detections):
        """计算统计信息"""
        stats = {
            "total": 0,
            "wearing_helmet": 0,
            "no_helmet": 0,
            "person": 0,
            "compliance_rate": 0.0,
        }

        for det in detections:
            class_name = det["class"]
            if class_name == "person":
                stats["person"] += 1
                stats["total"] += 1
            elif "helmet" in class_name.lower():
                stats["total"] += 1
                if "no" in class_name.lower() or "without" in class_name.lower():
                    stats["no_helmet"] += 1
                else:
                    stats["wearing_helmet"] += 1

        # 计算合规率
        if stats["total"] > 0:
            stats["compliance_rate"] = (stats["wearing_helmet"] / stats["total"]) * 100

        return stats

    def _draw_annotations(self, image, detections, statistics):
        """在图像上绘制检测框和标签"""
        for det in detections:
            bbox = det["bbox"]
            class_name = det["class"]
            confidence = det["confidence"]

            # 确定颜色（默认使用配置中的颜色）
            if class_name in CLASS_COLORS:
                color = CLASS_COLORS[class_name]
            elif "helmet" in class_name.lower():
                if "no" in class_name.lower():
                    color = (0, 0, 255)  # 红色 - 未佩戴
                else:
                    color = (0, 255, 0)  # 绿色 - 佩戴
            else:
                color = (255, 0, 0)  # 蓝色 - 人员

            # 绘制边界框
            cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)

            # 准备标签文本（中文）
            label_zh = CLASS_NAMES_ZH.get(class_name, class_name)
            label = f"{label_zh}: {confidence:.2f}"

            # 绘制标签背景
            image = self._draw_label(image, bbox, label, color)

        # 在图像顶部绘制统计信息
        info_text = (
            f"Total: {statistics['total']} | "
            f"Wearing: {statistics['wearing_helmet']} | "
            f"No Helmet: {statistics['no_helmet']} | "
            f"Rate: {statistics['compliance_rate']:.1f}%"
        )
        cv2.putText(
            image,
            info_text,
            (10, image.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        return image

    def set_confidence_threshold(self, threshold):
        """设置置信度阈值"""
        self.conf_threshold = threshold
        self.model.conf = threshold
        print(f"✓ 置信度阈值已设置为: {threshold}")

    def set_iou_threshold(self, threshold):
        """设置IoU阈值"""
        self.iou_threshold = threshold
        self.model.iou = threshold
        print(f"✓ IoU阈值已设置为: {threshold}")


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("安全帽检测器测试")
    print("=" * 60)

    try:
        # 创建检测器
        detector = HelmetDetector(device="cpu")  # 使用CPU进行测试

        print("\n✓ 检测器创建成功")
        print("提示: 请准备测试图片/视频进行检测")

    except Exception as e:
        print(f"\n✗ 检测器创建失败: {e}")
        import traceback

        traceback.print_exc()
