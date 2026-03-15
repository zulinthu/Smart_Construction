"""
视频处理工具函数
提供视频读取、写入、帧提取等功能
"""

import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm


def get_video_info(video_path):
    """
    获取视频信息
    
    Args:
        video_path: 视频路径
        
    Returns:
        info: 视频信息字典
    """
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        raise ValueError(f"无法打开视频: {video_path}")
    
    info = {
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'fps': int(cap.get(cv2.CAP_PROP_FPS)),
        'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        'duration': 0
    }
    
    if info['fps'] > 0:
        info['duration'] = info['frame_count'] / info['fps']
    
    cap.release()
    
    return info


def extract_frames(video_path, output_dir, interval=1, max_frames=None):
    """
    从视频中提取帧
    
    Args:
        video_path: 视频路径
        output_dir: 输出目录
        interval: 提取间隔（每N帧提取一帧）
        max_frames: 最大提取帧数
        
    Returns:
        frame_paths: 提取的帧路径列表
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cap = cv2.VideoCapture(str(video_path))
    frame_paths = []
    frame_idx = 0
    saved_count = 0
    
    try:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        pbar = tqdm(total=total_frames, desc="提取帧")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % interval == 0:
                frame_path = output_dir / f"frame_{frame_idx:06d}.jpg"
                cv2.imwrite(str(frame_path), frame)
                frame_paths.append(frame_path)
                saved_count += 1
                
                if max_frames and saved_count >= max_frames:
                    break
            
            frame_idx += 1
            pbar.update(1)
        
        pbar.close()
        
    finally:
        cap.release()
    
    print(f"✓ 提取完成: {saved_count} 帧")
    return frame_paths


def create_video_from_frames(frame_paths, output_path, fps=30):
    """
    从帧序列创建视频
    
    Args:
        frame_paths: 帧路径列表
        output_path: 输出视频路径
        fps: 帧率
    """
    if not frame_paths:
        raise ValueError("帧列表为空")
    
    # 读取第一帧以获取尺寸
    first_frame = cv2.imread(str(frame_paths[0]))
    height, width = first_frame.shape[:2]
    
    # 创建视频写入器
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    try:
        for frame_path in tqdm(frame_paths, desc="创建视频"):
            frame = cv2.imread(str(frame_path))
            if frame is not None:
                writer.write(frame)
    finally:
        writer.release()
    
    print(f"✓ 视频已保存: {output_path}")


def resize_video(input_path, output_path, target_size=(640, 480)):
    """
    调整视频尺寸
    
    Args:
        input_path: 输入视频路径
        output_path: 输出视频路径
        target_size: 目标尺寸 (width, height)
    """
    cap = cv2.VideoCapture(str(input_path))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, target_size)
    
    try:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        pbar = tqdm(total=total_frames, desc="调整视频尺寸")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            resized = cv2.resize(frame, target_size)
            writer.write(resized)
            pbar.update(1)
        
        pbar.close()
        
    finally:
        cap.release()
        writer.release()
    
    print(f"✓ 视频已保存: {output_path}")


def cut_video(input_path, output_path, start_time=0, end_time=None):
    """
    裁剪视频
    
    Args:
        input_path: 输入视频路径
        output_path: 输出视频路径
        start_time: 开始时间（秒）
        end_time: 结束时间（秒，None表示到结尾）
    """
    cap = cv2.VideoCapture(str(input_path))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps) if end_time else int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # 跳到开始帧
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    try:
        current_frame = start_frame
        pbar = tqdm(total=end_frame - start_frame, desc="裁剪视频")
        
        while current_frame < end_frame:
            ret, frame = cap.read()
            if not ret:
                break
            
            writer.write(frame)
            current_frame += 1
            pbar.update(1)
        
        pbar.close()
        
    finally:
        cap.release()
        writer.release()
    
    print(f"✓ 视频已保存: {output_path}")


def concatenate_videos(video_paths, output_path):
    """
    拼接多个视频
    
    Args:
        video_paths: 视频路径列表
        output_path: 输出视频路径
    """
    if not video_paths:
        raise ValueError("视频列表为空")
    
    # 获取第一个视频的属性
    cap = cv2.VideoCapture(str(video_paths[0]))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    try:
        for video_path in tqdm(video_paths, desc="拼接视频"):
            cap = cv2.VideoCapture(str(video_path))
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 确保尺寸一致
                if frame.shape[:2] != (height, width):
                    frame = cv2.resize(frame, (width, height))
                
                writer.write(frame)
            
            cap.release()
    
    finally:
        writer.release()
    
    print(f"✓ 视频已保存: {output_path}")


def add_text_to_video(input_path, output_path, text, position=(10, 30),
                      font_scale=1, color=(0, 255, 0), thickness=2):
    """
    在视频上添加文本
    
    Args:
        input_path: 输入视频路径
        output_path: 输出视频路径
        text: 文本内容
        position: 位置 (x, y)
        font_scale: 字体大小
        color: 颜色 (B, G, R)
        thickness: 线条粗细
    """
    cap = cv2.VideoCapture(str(input_path))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    try:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        pbar = tqdm(total=total_frames, desc="添加文本")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX,
                       font_scale, color, thickness, cv2.LINE_AA)
            
            writer.write(frame)
            pbar.update(1)
        
        pbar.close()
        
    finally:
        cap.release()
        writer.release()
    
    print(f"✓ 视频已保存: {output_path}")


class VideoCapture:
    """视频捕获类（支持进度条）"""
    
    def __init__(self, video_path, show_progress=True):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(str(video_path))
        self.show_progress = show_progress
        
        if not self.cap.isOpened():
            raise ValueError(f"无法打开视频: {video_path}")
        
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if show_progress:
            self.pbar = tqdm(total=self.frame_count, desc="处理视频")
        else:
            self.pbar = None
    
    def read(self):
        """读取下一帧"""
        ret, frame = self.cap.read()
        if ret and self.pbar:
            self.pbar.update(1)
        return ret, frame
    
    def release(self):
        """释放资源"""
        self.cap.release()
        if self.pbar:
            self.pbar.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


# 测试代码
if __name__ == '__main__':
    print("视频工具函数测试")
    print("=" * 60)
    print("✓ 所有工具函数已实现")
