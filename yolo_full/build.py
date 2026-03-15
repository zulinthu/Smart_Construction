#!/usr/bin/env python3
"""
安全帽检测系统 - Python构建脚本
跨平台构建管理工具（类似CMake）
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path


class Colors:
    """终端颜色"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color
    
    @staticmethod
    def disable():
        """Windows下禁用颜色"""
        if sys.platform == 'win32':
            Colors.RED = ''
            Colors.GREEN = ''
            Colors.YELLOW = ''
            Colors.BLUE = ''
            Colors.NC = ''


class Builder:
    """项目构建器"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.venv_dir = self.root_dir / 'venv'
        self.python = sys.executable
        
        # Windows下禁用颜色（除非使用Windows Terminal）
        if sys.platform == 'win32' and 'WT_SESSION' not in os.environ:
            Colors.disable()
    
    def print_section(self, message, color=Colors.GREEN):
        """打印分节信息"""
        print(f"\n{color}>>> {message}{Colors.NC}")
    
    def print_info(self, message):
        """打印信息"""
        print(f"{Colors.BLUE}{message}{Colors.NC}")
    
    def print_warning(self, message):
        """打印警告"""
        print(f"{Colors.YELLOW}{message}{Colors.NC}")
    
    def print_error(self, message):
        """打印错误"""
        print(f"{Colors.RED}{message}{Colors.NC}")
    
    def run_command(self, cmd, check=True, shell=False):
        """运行命令"""
        try:
            if isinstance(cmd, str):
                cmd = cmd.split()
            result = subprocess.run(cmd, check=check, shell=shell, 
                                   capture_output=False, text=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            self.print_error(f"命令执行失败: {e}")
            return False
        except Exception as e:
            self.print_error(f"错误: {e}")
            return False
    
    def init(self):
        """初始化项目"""
        self.print_section("初始化项目环境...")
        
        if self.venv_dir.exists():
            self.print_warning("虚拟环境已存在")
            return True
        
        # 创建虚拟环境
        if not self.run_command([self.python, '-m', 'venv', str(self.venv_dir)]):
            self.print_error("虚拟环境创建失败")
            return False
        
        self.print_info("✓ 虚拟环境创建完成")
        self.print_warning("请运行: python build.py install")
        return True
    
    def install(self):
        """安装依赖"""
        self.print_section("安装项目依赖...")
        
        # 升级pip
        self.run_command([self.python, '-m', 'pip', 'install', '--upgrade', 'pip'])
        
        # 安装依赖
        requirements_file = self.root_dir / 'requirements.txt'
        if not requirements_file.exists():
            self.print_error("requirements.txt 不存在")
            return False
        
        if not self.run_command([self.python, '-m', 'pip', 'install', '-r', str(requirements_file)]):
            self.print_error("依赖安装失败")
            return False
        
        # 初始化配置
        self.run_command([self.python, 'config.py'])
        
        self.print_info("✓ 依赖安装完成！")
        return True
    
    def install_dev(self):
        """安装开发依赖"""
        self.print_section("安装开发依赖...")
        
        dev_packages = ['black', 'flake8', 'pytest', 'pytest-cov']
        if not self.run_command([self.python, '-m', 'pip', 'install'] + dev_packages):
            self.print_error("开发依赖安装失败")
            return False
        
        self.print_info("✓ 开发依赖安装完成！")
        return True
    
    def setup_yolov5(self):
        """下载并配置YOLOv5"""
        self.print_section("下载YOLOv5源码...")
        
        yolov5_dir = self.root_dir / 'models' / 'yolov5'
        
        if yolov5_dir.exists():
            self.print_warning("YOLOv5已存在，跳过下载")
            return True
        
        # 克隆仓库
        models_dir = self.root_dir / 'models'
        models_dir.mkdir(exist_ok=True)
        
        if not self.run_command(['git', 'clone', 
                                'https://github.com/ultralytics/yolov5.git',
                                str(yolov5_dir)]):
            self.print_error("YOLOv5下载失败")
            return False
        
        # 安装YOLOv5依赖
        yolo_req = yolov5_dir / 'requirements.txt'
        if yolo_req.exists():
            self.run_command([self.python, '-m', 'pip', 'install', '-r', str(yolo_req)])
        
        self.print_info("✓ YOLOv5配置完成！")
        return True
    
    def download_weights(self):
        """下载预训练权重"""
        self.print_section("下载预训练权重...")
        
        weights_dir = self.root_dir / 'models' / 'weights'
        weights_dir.mkdir(parents=True, exist_ok=True)
        
        weights_file = weights_dir / 'yolov5s.pt'
        if weights_file.exists():
            self.print_warning("权重文件已存在，跳过下载")
            return True
        
        # 下载权重
        import urllib.request
        url = 'https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt'
        
        try:
            self.print_info("正在下载权重文件...")
            urllib.request.urlretrieve(url, str(weights_file))
            self.print_info("✓ 权重下载完成！")
            return True
        except Exception as e:
            self.print_error(f"权重下载失败: {e}")
            return False
    
    def build(self):
        """构建项目"""
        self.print_section("构建项目...")
        
        if not self.install():
            return False
        
        # 开发模式安装
        if not self.run_command([self.python, 'setup.py', 'develop']):
            self.print_error("项目构建失败")
            return False
        
        self.print_info("✓ 项目构建完成！")
        return True
    
    def clean(self):
        """清理临时文件"""
        self.print_section("清理临时文件...")
        
        patterns = [
            '**/__pycache__',
            '**/*.pyc',
            '**/*.pyo',
            '**/*.egg-info',
            'build',
            'dist',
            '.pytest_cache',
            '.coverage',
            'htmlcov'
        ]
        
        for pattern in patterns:
            for path in self.root_dir.glob(pattern):
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    path.unlink(missing_ok=True)
        
        self.print_info("✓ 清理完成！")
        return True
    
    def clean_all(self):
        """深度清理"""
        self.print_section("深度清理...", Colors.RED)
        
        self.clean()
        
        # 删除虚拟环境
        if self.venv_dir.exists():
            shutil.rmtree(self.venv_dir, ignore_errors=True)
        
        # 删除实验结果
        experiments_dir = self.root_dir / 'results' / 'experiments'
        if experiments_dir.exists():
            shutil.rmtree(experiments_dir, ignore_errors=True)
        
        self.print_info("✓ 深度清理完成！")
        return True
    
    def run(self):
        """运行主程序"""
        return self.run_command([self.python, 'run.py'])
    
    def gui(self):
        """启动GUI"""
        self.print_section("启动GUI界面...")
        return self.run_command([self.python, 'app/main.py'])
    
    def train_baseline(self):
        """训练基线模型"""
        self.print_section("训练基线模型...")
        return self.run_command([
            self.python, 'train/train_baseline.py',
            '--data', 'data/helmet.yaml',
            '--weights', 'models/weights/yolov5s.pt',
            '--epochs', '100',
            '--batch-size', '16'
        ])
    
    def test(self):
        """运行测试"""
        self.print_section("运行测试...")
        return self.run_command([self.python, '-m', 'pytest', 'tests/', '-v'])
    
    def test_camera(self):
        """测试摄像头"""
        self.print_section("测试摄像头...")
        code = """
from app.utils.video_utils import test_camera, get_camera_list
cameras = get_camera_list()
print(f'可用摄像头: {cameras}')
if cameras:
    test_camera(cameras[0], 5)
else:
    print('无摄像头')
"""
        return self.run_command([self.python, '-c', code])
    
    def format(self):
        """格式化代码"""
        self.print_section("格式化代码...")
        return self.run_command([
            self.python, '-m', 'black', '.',
            '--exclude', '/(\.git|venv|models/yolov5)/'
        ])
    
    def lint(self):
        """代码检查"""
        self.print_section("代码检查...")
        return self.run_command([
            self.python, '-m', 'flake8', '.',
            '--exclude', 'venv,models/yolov5',
            '--max-line-length', '100'
        ])
    
    def info(self):
        """显示项目信息"""
        print(f"\n{Colors.BLUE}{'='*40}{Colors.NC}")
        print(f"{Colors.GREEN}  项目信息{Colors.NC}")
        print(f"{Colors.BLUE}{'='*40}{Colors.NC}")
        print(f"项目名称: helmet-detection")
        print(f"Python: {sys.version.split()[0]}")
        print(f"工作目录: {self.root_dir}")
        print(f"{Colors.BLUE}{'='*40}{Colors.NC}\n")
        return True
    
    def check_env(self):
        """检查环境"""
        self.print_section("检查环境配置...")
        
        checks = [
            ("Python", "import sys; print(f'Python: {sys.version}')"),
            ("PyTorch", "import torch; print(f'PyTorch: {torch.__version__}')"),
            ("CUDA", "import torch; print(f'CUDA: {torch.cuda.is_available()}')"),
            ("OpenCV", "import cv2; print(f'OpenCV: {cv2.__version__}')"),
            ("PyQt5", "from PyQt5.QtCore import QT_VERSION_STR; print(f'PyQt5: {QT_VERSION_STR}')")
        ]
        
        for name, code in checks:
            try:
                subprocess.run([self.python, '-c', code], 
                             check=True, capture_output=True, text=True)
            except:
                print(f"{name}: 未安装")
        
        return True
    
    def all(self):
        """一键安装"""
        self.print_section("一键安装所有内容...")
        
        steps = [
            ('init', self.init),
            ('install', self.install),
            ('setup-yolov5', self.setup_yolov5),
            ('download-weights', self.download_weights),
        ]
        
        for name, func in steps:
            if not func():
                self.print_error(f"步骤失败: {name}")
                return False
        
        self.print_info("✓ 项目配置完成！")
        self.print_warning("运行 'python build.py gui' 启动应用")
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='安全帽检测系统 - 构建管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python build.py init              初始化项目
  python build.py install           安装依赖
  python build.py all               一键安装
  python build.py gui               启动GUI
  python build.py clean             清理临时文件
        """
    )
    
    parser.add_argument('command', nargs='?', default='help',
                       help='要执行的命令')
    
    args = parser.parse_args()
    
    builder = Builder()
    
    # 命令映射
    commands = {
        'help': lambda: parser.print_help(),
        'init': builder.init,
        'install': builder.install,
        'install-dev': builder.install_dev,
        'setup-yolov5': builder.setup_yolov5,
        'download-weights': builder.download_weights,
        'build': builder.build,
        'clean': builder.clean,
        'clean-all': builder.clean_all,
        'run': builder.run,
        'gui': builder.gui,
        'train-baseline': builder.train_baseline,
        'test': builder.test,
        'test-camera': builder.test_camera,
        'format': builder.format,
        'lint': builder.lint,
        'info': builder.info,
        'check-env': builder.check_env,
        'all': builder.all,
    }
    
    command = args.command.lower()
    
    if command not in commands:
        builder.print_error(f"未知命令: {command}")
        parser.print_help()
        return 1
    
    try:
        success = commands[command]()
        return 0 if success else 1
    except KeyboardInterrupt:
        builder.print_warning("\n\n用户中断")
        return 130
    except Exception as e:
        builder.print_error(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())










