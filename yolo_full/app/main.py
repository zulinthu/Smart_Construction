"""
安全帽检测系统 - 主程序入口
基于PyQt5的图形界面应用
"""

import sys
import os
from pathlib import Path

# 设置Windows控制台UTF-8编码支持
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from app.ui.main_window import MainWindow
from config import init_directories, print_config, FONT_FAMILY, FONT_SIZE


def setup_app():
    """设置应用程序"""
    # 初始化目录
    init_directories()

    # 打印配置信息
    print_config()

    # 创建应用
    app = QApplication(sys.argv)

    # 设置应用属性
    app.setApplicationName("安全帽检测系统")
    app.setApplicationDisplayName("安全帽检测系统 v1.0")
    app.setOrganizationName("Your Organization")

    # 设置高DPI支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 设置全局字体
    font = QFont(FONT_FAMILY, FONT_SIZE)
    app.setFont(font)

    # 设置样式表
    app.setStyleSheet(get_stylesheet())

    return app


def get_stylesheet():
    """获取应用样式表"""
    return """
    QMainWindow {
        background-color: #f5f5f5;
    }

    QPushButton {
        background-color: #2196F3;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-size: 12px;
        min-width: 80px;
    }

    QPushButton:hover {
        background-color: #1976D2;
    }

    QPushButton:pressed {
        background-color: #0D47A1;
    }

    QPushButton:disabled {
        background-color: #BDBDBD;
        color: #757575;
    }

    QGroupBox {
        border: 2px solid #E0E0E0;
        border-radius: 5px;
        margin-top: 10px;
        padding-top: 10px;
        font-weight: bold;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }

    QLabel {
        color: #333333;
    }

    QLineEdit {
        border: 1px solid #BDBDBD;
        border-radius: 3px;
        padding: 5px;
        background-color: white;
    }

    QLineEdit:focus {
        border: 2px solid #2196F3;
    }

    QComboBox {
        border: 1px solid #BDBDBD;
        border-radius: 3px;
        padding: 5px;
        background-color: white;
    }

    QSlider::groove:horizontal {
        height: 6px;
        background: #E0E0E0;
        border-radius: 3px;
    }

    QSlider::handle:horizontal {
        background: #2196F3;
        width: 16px;
        height: 16px;
        margin: -5px 0;
        border-radius: 8px;
    }

    QTextEdit {
        border: 1px solid #BDBDBD;
        border-radius: 3px;
        background-color: white;
        font-family: Consolas, monospace;
        font-size: 10px;
    }

    QStatusBar {
        background-color: #424242;
        color: white;
    }

    QProgressBar {
        border: 1px solid #BDBDBD;
        border-radius: 3px;
        text-align: center;
        background-color: #E0E0E0;
    }

    QProgressBar::chunk {
        background-color: #4CAF50;
        border-radius: 2px;
    }
    """


def main():
    """主函数"""
    try:
        # 设置应用
        app = setup_app()

        # 创建主窗口
        window = MainWindow()
        window.show()

        print("\n✓ 应用启动成功")
        print("=" * 60)

        # 运行应用
        sys.exit(app.exec_())

    except Exception as e:
        print(f"\n✗ 应用启动失败: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
