"""
YOLOv5模型下载工具
帮助用户下载预训练模型权重
"""

import sys
import importlib
from pathlib import Path
import urllib.request
import ssl

# 添加项目根目录
ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

config = importlib.import_module("config")
WEIGHTS_DIR = config.WEIGHTS_DIR

# 模型下载链接（GitHub Release）
MODEL_URLS = {
    "yolov5n": "https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5n.pt",
    "yolov5s": "https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt",
    "yolov5m": "https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5m.pt",
    "yolov5l": "https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5l.pt",
    "yolov5x": "https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5x.pt",
}

# 模型大小信息
MODEL_SIZES = {
    "yolov5n": "3.9 MB  (最快，精度较低)",
    "yolov5s": "14.4 MB (推荐，平衡)",
    "yolov5m": "40.8 MB (中等)",
    "yolov5l": "89.3 MB (大型)",
    "yolov5x": "166 MB  (最大，最精确)",
}


def download_file(url, save_path, show_progress=True):
    """
    下载文件

    Args:
        url: 下载链接
        save_path: 保存路径
        show_progress: 是否显示进度
    """
    # 创建SSL上下文（忽略证书验证，仅用于下载）
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    def show_download_progress(downloaded, total_size):
        """显示下载进度"""
        if total_size > 0:
            percent = min(downloaded * 100 / total_size, 100)
            bar_length = 50
            filled = int(bar_length * percent / 100)
            bar = "█" * filled + "-" * (bar_length - filled)

            # 转换为MB
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total_size / (1024 * 1024)

            print(
                f"\r下载进度: |{bar}| {percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)",
                end="",
            )
        else:
            downloaded_mb = downloaded / (1024 * 1024)
            print(f"\r下载中: {downloaded_mb:.1f} MB", end="")

    try:
        if show_progress:
            print(f"开始下载: {url}")

        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        chunk_size = 8192
        downloaded = 0

        with urllib.request.urlopen(url, context=ssl_context) as response, open(
            save_path, "wb"
        ) as f:
            total_size = int(response.headers.get("Content-Length", "0"))

            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if show_progress:
                    show_download_progress(downloaded, total_size)

        if show_progress:
            print()  # 换行

        return True
    except Exception as e:
        print(f"\n下载失败: {e}")
        return False


def download_model(model_name="yolov5s"):
    """
    下载指定的YOLOv5模型

    Args:
        model_name: 模型名称
    """
    if model_name not in MODEL_URLS:
        print(f"错误: 未知的模型名称 '{model_name}'")
        print(f"可用的模型: {', '.join(MODEL_URLS.keys())}")
        return False

    # 创建权重目录
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)

    # 下载路径
    save_path = WEIGHTS_DIR / f"{model_name}.pt"

    # 检查是否已存在
    if save_path.exists():
        print(f"模型已存在: {save_path}")
        choice = input("是否重新下载? (y/n): ").lower()
        if choice != "y":
            print("跳过下载")
            return True
        save_path.unlink()  # 删除旧文件

    # 下载模型
    url = MODEL_URLS[model_name]
    print(f"\n下载模型: {model_name}")
    print(f"大小: {MODEL_SIZES[model_name]}")
    print(f"保存到: {save_path}\n")

    success = download_file(url, save_path)

    if success:
        print(f"✓ 下载成功: {save_path}")
        print("\n使用方法:")
        print("  from app.core.detector import HelmetDetector")
        print(f"  detector = HelmetDetector(weights_path='{save_path}')")
        return True
    else:
        print("✗ 下载失败")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("YOLOv5模型下载工具")
    print("=" * 60)
    print()

    # 显示可用模型
    print("可用的模型:")
    print("-" * 60)
    for name, size in MODEL_SIZES.items():
        print(f"  {name:10s} - {size}")
    print("-" * 60)
    print()

    # 获取用户选择
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
    else:
        model_name = input("请选择要下载的模型 [yolov5s]: ").strip() or "yolov5s"

    # 下载模型
    success = download_model(model_name)

    if not success:
        print("\n" + "=" * 60)
        print("备选方案:")
        print("=" * 60)
        print("1. 手动下载:")
        print("   访问: https://github.com/ultralytics/yolov5/releases")
        print(f"   下载 {model_name}.pt")
        print(f"   放到: {WEIGHTS_DIR}")
        print()
        print("2. 使用浏览器下载:")
        if model_name in MODEL_URLS:
            print(f"   {MODEL_URLS[model_name]}")
        print()
        print("3. 使用代理或VPN")
        print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户取消下载")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback

        traceback.print_exc()
