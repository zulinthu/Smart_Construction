#!/bin/bash
# ========================================
# 安全帽检测系统 - Linux/Mac构建脚本
# 类似CMake的项目构建管理
# ========================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="helmet-detection"
PYTHON="python3"
PIP="pip3"
VENV="venv"

# 帮助函数
show_help() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${GREEN}  安全帽检测系统 - 构建系统${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    echo "使用方法: ./build.sh [command]"
    echo ""
    echo -e "${YELLOW}环境设置:${NC}"
    echo "  init              - 初始化项目（首次使用）"
    echo "  install           - 安装所有依赖"
    echo "  install-dev       - 安装开发依赖"
    echo "  setup-yolov5      - 下载并配置YOLOv5"
    echo "  download-weights  - 下载预训练权重"
    echo ""
    echo -e "${YELLOW}项目构建:${NC}"
    echo "  build             - 构建项目"
    echo "  clean             - 清理临时文件"
    echo "  clean-all         - 深度清理（包括虚拟环境）"
    echo ""
    echo -e "${YELLOW}运行程序:${NC}"
    echo "  run               - 运行主程序"
    echo "  gui               - 启动GUI界面"
    echo ""
    echo -e "${YELLOW}训练与评估:${NC}"
    echo "  train-baseline    - 训练基线模型"
    echo "  train-improved    - 训练改进模型"
    echo "  eval              - 评估模型"
    echo "  compare           - 对比模型性能"
    echo ""
    echo -e "${YELLOW}测试:${NC}"
    echo "  test              - 运行测试"
    echo "  test-camera       - 测试摄像头"
    echo ""
    echo -e "${YELLOW}代码质量:${NC}"
    echo "  format            - 格式化代码"
    echo "  lint              - 代码检查"
    echo ""
    echo -e "${YELLOW}工具:${NC}"
    echo "  tensorboard       - 启动TensorBoard"
    echo "  info              - 显示项目信息"
    echo "  check-env         - 检查环境配置"
    echo ""
    echo -e "${YELLOW}快速开始:${NC}"
    echo "  all               - 一键安装所有内容"
    echo ""
}

# 初始化项目
init() {
    echo -e "${GREEN}>>> 初始化项目环境...${NC}"
    $PYTHON -m venv $VENV
    echo -e "${GREEN}>>> 虚拟环境创建完成${NC}"
    echo -e "${YELLOW}>>> 激活虚拟环境: source $VENV/bin/activate${NC}"
    echo -e "${YELLOW}>>> 然后运行: ./build.sh install${NC}"
}

# 安装依赖
install() {
    echo -e "${GREEN}>>> 安装项目依赖...${NC}"
    $PIP install --upgrade pip
    $PIP install -r requirements.txt
    $PYTHON config.py
    echo -e "${GREEN}>>> 依赖安装完成！${NC}"
}

# 安装开发依赖
install_dev() {
    echo -e "${GREEN}>>> 安装开发依赖...${NC}"
    $PIP install black flake8 pytest pytest-cov
    echo -e "${GREEN}>>> 开发依赖安装完成！${NC}"
}

# 下载YOLOv5
setup_yolov5() {
    echo -e "${GREEN}>>> 下载YOLOv5源码...${NC}"
    if [ ! -d "models/yolov5" ]; then
        cd models
        git clone https://github.com/ultralytics/yolov5.git
        cd yolov5
        $PIP install -r requirements.txt
        cd ../..
        echo -e "${GREEN}>>> YOLOv5配置完成！${NC}"
    else
        echo -e "${YELLOW}YOLOv5已存在，跳过下载${NC}"
    fi
}

# 下载预训练权重
download_weights() {
    echo -e "${GREEN}>>> 下载预训练权重...${NC}"
    mkdir -p models/weights
    wget -O models/weights/yolov5s.pt https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt
    echo -e "${GREEN}>>> 权重下载完成！${NC}"
}

# 构建项目
build() {
    echo -e "${GREEN}>>> 构建项目...${NC}"
    install
    $PYTHON setup.py develop
    echo -e "${GREEN}>>> 项目构建完成！${NC}"
}

# 清理临时文件
clean() {
    echo -e "${YELLOW}>>> 清理临时文件...${NC}"
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/ 2>/dev/null || true
    echo -e "${GREEN}>>> 清理完成！${NC}"
}

# 深度清理
clean_all() {
    echo -e "${RED}>>> 深度清理...${NC}"
    clean
    rm -rf $VENV 2>/dev/null || true
    rm -rf results/experiments/* 2>/dev/null || true
    echo -e "${GREEN}>>> 深度清理完成！${NC}"
}

# 运行主程序
run() {
    $PYTHON run.py
}

# 启动GUI
gui() {
    echo -e "${GREEN}>>> 启动GUI界面...${NC}"
    $PYTHON app/main.py
}

# 训练基线模型
train_baseline() {
    echo -e "${GREEN}>>> 训练基线模型...${NC}"
    $PYTHON train/train_baseline.py \
        --data data/helmet.yaml \
        --weights models/weights/yolov5s.pt \
        --epochs 100 \
        --batch-size 16
}

# 训练改进模型
train_improved() {
    echo -e "${GREEN}>>> 训练改进模型...${NC}"
    $PYTHON train/train_improved.py \
        --data data/helmet.yaml \
        --epochs 100 \
        --batch-size 16
}

# 评估模型
eval() {
    echo -e "${GREEN}>>> 评估模型...${NC}"
    $PYTHON evaluate/eval_model.py \
        --weights models/weights/improved_final.pt \
        --data data/helmet.yaml
}

# 对比模型
compare() {
    echo -e "${GREEN}>>> 对比模型性能...${NC}"
    $PYTHON evaluate/compare_models.py
}

# 运行测试
test() {
    echo -e "${GREEN}>>> 运行测试...${NC}"
    $PYTHON -m pytest tests/ -v
}

# 测试摄像头
test_camera() {
    echo -e "${GREEN}>>> 测试摄像头...${NC}"
    $PYTHON -c "from app.utils.video_utils import test_camera, get_camera_list; cameras = get_camera_list(); print(f'可用摄像头: {cameras}'); test_camera(cameras[0], 5) if cameras else print('无摄像头')"
}

# 格式化代码
format() {
    echo -e "${GREEN}>>> 格式化代码...${NC}"
    $PYTHON -m black . --exclude="/(\.git|venv|models/yolov5)/"
    echo -e "${GREEN}>>> 代码格式化完成！${NC}"
}

# 代码检查
lint() {
    echo -e "${GREEN}>>> 代码检查...${NC}"
    $PYTHON -m flake8 . --exclude=venv,models/yolov5 --max-line-length=100
}

# TensorBoard
tensorboard() {
    echo -e "${GREEN}>>> 启动TensorBoard...${NC}"
    tensorboard --logdir results/experiments --port 6006
}

# 显示项目信息
info() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${GREEN}  项目信息${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo "项目名称: $PROJECT_NAME"
    $PYTHON --version
    $PIP --version
    echo "工作目录: $(pwd)"
    echo -e "${BLUE}========================================${NC}\n"
}

# 检查环境
check_env() {
    echo -e "${GREEN}>>> 检查环境配置...${NC}"
    $PYTHON -c "import sys; print(f'Python: {sys.version}')"
    $PYTHON -c "import torch; print(f'PyTorch: {torch.__version__}')" 2>/dev/null || echo "PyTorch: 未安装"
    $PYTHON -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')" 2>/dev/null || echo "CUDA: 未安装"
    $PYTHON -c "import cv2; print(f'OpenCV: {cv2.__version__}')" 2>/dev/null || echo "OpenCV: 未安装"
    $PYTHON -c "from PyQt5.QtCore import QT_VERSION_STR; print(f'PyQt5: {QT_VERSION_STR}')" 2>/dev/null || echo "PyQt5: 未安装"
}

# 一键安装
all() {
    echo -e "${GREEN}>>> 一键安装所有内容...${NC}"
    init
    echo -e "${YELLOW}>>> 激活虚拟环境: source $VENV/bin/activate${NC}"
    install
    setup_yolov5
    download_weights
    echo -e "${GREEN}>>> 项目配置完成！${NC}"
    echo -e "${YELLOW}>>> 运行 './build.sh gui' 启动应用${NC}"
}

# 主函数
main() {
    case "$1" in
        help|--help|-h)
            show_help
            ;;
        init)
            init
            ;;
        install)
            install
            ;;
        install-dev)
            install_dev
            ;;
        setup-yolov5)
            setup_yolov5
            ;;
        download-weights)
            download_weights
            ;;
        build)
            build
            ;;
        clean)
            clean
            ;;
        clean-all)
            clean_all
            ;;
        run)
            run
            ;;
        gui)
            gui
            ;;
        train-baseline)
            train_baseline
            ;;
        train-improved)
            train_improved
            ;;
        eval)
            eval
            ;;
        compare)
            compare
            ;;
        test)
            test
            ;;
        test-camera)
            test_camera
            ;;
        format)
            format
            ;;
        lint)
            lint
            ;;
        tensorboard)
            tensorboard
            ;;
        info)
            info
            ;;
        check-env)
            check_env
            ;;
        all)
            all
            ;;
        "")
            show_help
            ;;
        *)
            echo -e "${RED}错误：未知命令 '$1'${NC}"
            echo "运行 './build.sh help' 查看帮助"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"










