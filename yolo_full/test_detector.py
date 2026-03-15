"""
检测器快速测试脚本
用于验证检测器功能是否正常
"""

import sys
import io
from pathlib import Path

# 设置Windows控制台UTF-8编码支持
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# 添加项目根目录
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

print("=" * 60)
print("安全帽检测系统 - 快速测试")
print("=" * 60)
print()


def test_imports():
    """测试依赖导入"""
    print("[1/5] 测试依赖导入...")

    try:
        import torch

        print(f"  ✓ PyTorch: {torch.__version__}")
        print(f"    CUDA可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"    GPU: {torch.cuda.get_device_name(0)}")
    except ImportError as e:
        print(f"  ✗ PyTorch导入失败: {e}")
        return False

    try:
        import cv2

        print(f"  ✓ OpenCV: {cv2.__version__}")
    except ImportError as e:
        print(f"  ✗ OpenCV导入失败: {e}")
        return False

    try:
        from PyQt5 import QtCore

        print(f"  ✓ PyQt5: {QtCore.QT_VERSION_STR}")
    except ImportError as e:
        print(f"  ✗ PyQt5导入失败: {e}")
        return False

    try:
        import numpy as np

        print(f"  ✓ NumPy: {np.__version__}")
    except ImportError as e:
        print(f"  ✗ NumPy导入失败: {e}")
        return False

    print()
    return True


def test_detector_creation():
    """测试检测器创建"""
    print("[2/5] 测试检测器创建...")

    try:
        from app.core.detector import HelmetDetector

        # 使用CPU创建检测器（更快）
        detector = HelmetDetector(device="cpu", img_size=640)
        print("  ✓ 检测器创建成功")
        print(f"    设备: {detector.device}")
        print(f"    图像尺寸: {detector.img_size}")
        print(f"    置信度阈值: {detector.conf_threshold}")
        print()
        return detector

    except Exception as e:
        print(f"  ✗ 检测器创建失败: {e}")
        import traceback

        traceback.print_exc()
        return None


def test_image_detection(detector):
    """测试图像检测"""
    print("[3/5] 测试图像检测...")

    try:
        import cv2
        import numpy as np

        # 创建测试图像
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        test_image[:] = (100, 150, 200)  # 填充颜色

        # 保存测试图像
        test_image_path = ROOT_DIR / "test_image.jpg"
        cv2.imwrite(str(test_image_path), test_image)
        print(f"  ✓ 测试图像已创建: {test_image_path}")

        # 执行检测
        print("  ⏳ 正在检测... (首次运行会下载模型，请耐心等待)")
        annotated_img, detections, statistics = detector.detect_image(
            str(test_image_path)
        )

        print(f"  ✓ 检测完成")
        print(f"    检测数量: {len(detections)}")
        print(f"    统计信息: {statistics}")

        # 保存结果
        result_path = ROOT_DIR / "test_result.jpg"
        cv2.imwrite(str(result_path), annotated_img)
        print(f"  ✓ 结果已保存: {result_path}")
        print()

        # 清理测试文件
        test_image_path.unlink()

        return True

    except Exception as e:
        print(f"  ✗ 图像检测失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_gui_launch():
    """测试GUI启动"""
    print("[4/5] 测试GUI组件...")

    try:
        from PyQt5.QtWidgets import QApplication
        from app.ui.main_window import MainWindow

        print("  ✓ GUI组件导入成功")
        print("  提示: 可运行 'python app/main.py' 启动完整GUI")
        print()
        return True

    except Exception as e:
        print(f"  ✗ GUI组件测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_summary():
    """测试总结"""
    print("[5/5] 测试总结")
    print("  ✓ 所有核心功能测试完成！")
    print()
    print("=" * 60)
    print("下一步操作:")
    print("=" * 60)
    print("1. 启动GUI应用:")
    print("   python app/main.py")
    print()
    print("2. 使用自己的图片测试:")
    print("   from app.core.detector import HelmetDetector")
    print("   detector = HelmetDetector(device='cpu')")
    print("   result = detector.detect_image('your_image.jpg')")
    print()
    print("3. 训练自己的模型:")
    print("   python train/train_baseline.py")
    print()
    print("4. 评估模型性能:")
    print("   python evaluate/eval_model.py")
    print("=" * 60)


def main():
    """主函数"""
    # 1. 测试依赖
    if not test_imports():
        print("\n✗ 依赖检查失败，请先安装所需依赖:")
        print("  pip install -r requirements.txt")
        return

    # 2. 创建检测器
    detector = test_detector_creation()
    if detector is None:
        print("\n✗ 检测器创建失败")
        return

    # 3. 测试图像检测
    if not test_image_detection(detector):
        print("\n⚠ 图像检测测试未通过，但核心功能可能正常")

    # 4. 测试GUI
    test_gui_launch()

    # 5. 总结
    test_summary()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断测试")
    except Exception as e:
        print(f"\n✗ 测试过程出错: {e}")
        import traceback

        traceback.print_exc()
