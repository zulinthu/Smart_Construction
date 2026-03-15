"""
图像处理工具函数
提供图像读取、保存、格式转换等功能
"""

import cv2
import numpy as np
from pathlib import Path
from PIL import Image


def read_image(image_path):
    """
    读取图像文件
    
    Args:
        image_path: 图像路径
        
    Returns:
        image: OpenCV格式的图像(BGR)
    """
    image_path = Path(image_path)
    
    if not image_path.exists():
        raise FileNotFoundError(f"图像文件不存在: {image_path}")
    
    # 使用OpenCV读取
    image = cv2.imread(str(image_path))
    
    if image is None:
        # 尝试使用PIL读取（支持更多格式）
        try:
            pil_image = Image.open(image_path)
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            raise ValueError(f"无法读取图像: {image_path}, 错误: {e}")
    
    return image


def save_image(image, save_path, quality=95):
    """
    保存图像文件
    
    Args:
        image: OpenCV格式的图像(BGR)
        save_path: 保存路径
        quality: JPEG质量(1-100)
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 根据文件扩展名设置保存参数
    ext = save_path.suffix.lower()
    
    if ext in ['.jpg', '.jpeg']:
        cv2.imwrite(str(save_path), image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    elif ext == '.png':
        cv2.imwrite(str(save_path), image, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    else:
        cv2.imwrite(str(save_path), image)
    
    return save_path


def resize_image(image, target_size=640, keep_ratio=True):
    """
    调整图像大小
    
    Args:
        image: 输入图像
        target_size: 目标尺寸
        keep_ratio: 是否保持宽高比
        
    Returns:
        resized_image: 调整后的图像
    """
    h, w = image.shape[:2]
    
    if keep_ratio:
        # 计算缩放比例
        scale = target_size / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # 创建正方形画布并居中放置
        canvas = np.zeros((target_size, target_size, 3), dtype=np.uint8)
        y_offset = (target_size - new_h) // 2
        x_offset = (target_size - new_w) // 2
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        
        return canvas
    else:
        return cv2.resize(image, (target_size, target_size), interpolation=cv2.INTER_LINEAR)


def crop_image(image, bbox):
    """
    裁剪图像
    
    Args:
        image: 输入图像
        bbox: 边界框 [x1, y1, x2, y2]
        
    Returns:
        cropped: 裁剪后的图像
    """
    x1, y1, x2, y2 = bbox
    return image[y1:y2, x1:x2]


def opencv_to_pil(image):
    """
    OpenCV图像转PIL图像
    
    Args:
        image: OpenCV图像(BGR)
        
    Returns:
        pil_image: PIL图像(RGB)
    """
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(image_rgb)


def pil_to_opencv(pil_image):
    """
    PIL图像转OpenCV图像
    
    Args:
        pil_image: PIL图像(RGB)
        
    Returns:
        image: OpenCV图像(BGR)
    """
    image_rgb = np.array(pil_image)
    return cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)


def add_chinese_text(image, text, position, font_size=20, color=(255, 255, 255)):
    """
    在图像上添加中文文本（使用PIL）
    
    Args:
        image: OpenCV图像
        text: 文本内容
        position: 位置 (x, y)
        font_size: 字体大小
        color: 颜色 (B, G, R)
        
    Returns:
        image: 添加文本后的图像
    """
    from PIL import ImageDraw, ImageFont
    
    # 转换为PIL图像
    pil_img = opencv_to_pil(image)
    draw = ImageDraw.Draw(pil_img)
    
    # 尝试使用中文字体
    try:
        # Windows系统字体
        font = ImageFont.truetype("msyh.ttc", font_size)
    except:
        try:
            font = ImageFont.truetype("simhei.ttf", font_size)
        except:
            # 使用默认字体
            font = ImageFont.load_default()
    
    # BGR转RGB颜色
    color_rgb = (color[2], color[1], color[0])
    draw.text(position, text, font=font, fill=color_rgb)
    
    # 转回OpenCV格式
    return pil_to_opencv(pil_img)


def create_mosaic(images, grid_size=(2, 2)):
    """
    创建图像拼接网格
    
    Args:
        images: 图像列表
        grid_size: 网格大小 (rows, cols)
        
    Returns:
        mosaic: 拼接后的图像
    """
    rows, cols = grid_size
    
    if len(images) > rows * cols:
        images = images[:rows * cols]
    
    # 调整所有图像到相同大小
    h, w = images[0].shape[:2]
    resized_images = [cv2.resize(img, (w, h)) for img in images]
    
    # 填充不足的网格
    while len(resized_images) < rows * cols:
        resized_images.append(np.zeros_like(resized_images[0]))
    
    # 创建行
    row_images = []
    for i in range(rows):
        row = np.hstack(resized_images[i*cols:(i+1)*cols])
        row_images.append(row)
    
    # 垂直拼接
    mosaic = np.vstack(row_images)
    
    return mosaic


def draw_detection_box(image, bbox, label, confidence, color=(0, 255, 0)):
    """
    绘制检测框
    
    Args:
        image: 输入图像
        bbox: 边界框 [x1, y1, x2, y2]
        label: 标签文本
        confidence: 置信度
        color: 颜色 (B, G, R)
        
    Returns:
        image: 绘制后的图像
    """
    x1, y1, x2, y2 = bbox
    
    # 绘制矩形框
    cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
    
    # 准备标签
    text = f"{label}: {confidence:.2f}"
    
    # 计算文本大小
    (text_w, text_h), baseline = cv2.getTextSize(
        text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1
    )
    
    # 绘制标签背景
    cv2.rectangle(
        image,
        (x1, y1 - text_h - 10),
        (x1 + text_w, y1),
        color,
        -1
    )
    
    # 绘制文本
    cv2.putText(
        image,
        text,
        (x1, y1 - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        1,
        cv2.LINE_AA
    )
    
    return image


def apply_colormap(image, colormap=cv2.COLORMAP_JET):
    """
    应用伪彩色映射
    
    Args:
        image: 灰度图像
        colormap: 颜色映射类型
        
    Returns:
        colored: 伪彩色图像
    """
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    return cv2.applyColorMap(image, colormap)


def enhance_image(image, brightness=1.0, contrast=1.0, saturation=1.0):
    """
    增强图像
    
    Args:
        image: 输入图像
        brightness: 亮度系数 (0.0 - 2.0)
        contrast: 对比度系数 (0.0 - 2.0)
        saturation: 饱和度系数 (0.0 - 2.0)
        
    Returns:
        enhanced: 增强后的图像
    """
    # 亮度和对比度调整
    enhanced = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness * 50)
    
    # 饱和度调整
    if saturation != 1.0:
        hsv = cv2.cvtColor(enhanced, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = hsv[:, :, 1] * saturation
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
        enhanced = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    
    return enhanced


# 测试代码
if __name__ == '__main__':
    print("图像工具函数测试")
    print("=" * 60)
    
    # 创建测试图像
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    test_image[:] = (100, 150, 200)  # 填充颜色
    
    # 测试绘制检测框
    test_image = draw_detection_box(
        test_image,
        bbox=[100, 100, 300, 300],
        label="测试对象",
        confidence=0.95,
        color=(0, 255, 0)
    )
    
    print("✓ 绘制检测框成功")
    print("✓ 所有工具函数已实现")
