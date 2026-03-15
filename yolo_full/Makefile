# 安全帽检测系统 - Makefile构建脚本
# 类似CMake的项目构建管理

.PHONY: help init install clean test run train eval gui format lint docs build docker

# 默认目标
.DEFAULT_GOAL := help

# 项目配置
PROJECT_NAME = helmet-detection
PYTHON = python
PIP = pip
VENV = venv
VENV_ACTIVATE = $(VENV)/Scripts/activate

# 颜色输出
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

##@ 帮助信息

help: ## 显示帮助信息
	@echo "$(BLUE)========================================$(NC)"
	@echo "$(GREEN)  安全帽检测系统 - 构建系统$(NC)"
	@echo "$(BLUE)========================================$(NC)"
	@echo ""
	@echo "使用方法: make [target]"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ 环境设置

init: ## 初始化项目（首次使用）
	@echo "$(GREEN)>>> 初始化项目环境...$(NC)"
	@$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)>>> 虚拟环境创建完成$(NC)"
	@echo "$(YELLOW)>>> 请运行: make install$(NC)"

install: ## 安装所有依赖
	@echo "$(GREEN)>>> 安装项目依赖...$(NC)"
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@$(PYTHON) config.py
	@echo "$(GREEN)>>> 依赖安装完成！$(NC)"

install-dev: ## 安装开发依赖
	@echo "$(GREEN)>>> 安装开发依赖...$(NC)"
	@$(PIP) install black flake8 pytest pytest-cov
	@echo "$(GREEN)>>> 开发依赖安装完成！$(NC)"

setup-yolov5: ## 下载并配置YOLOv5
	@echo "$(GREEN)>>> 下载YOLOv5源码...$(NC)"
	@if [ ! -d "models/yolov5" ]; then \
		cd models && git clone https://github.com/ultralytics/yolov5.git; \
	else \
		echo "$(YELLOW)YOLOv5已存在，跳过下载$(NC)"; \
	fi
	@cd models/yolov5 && $(PIP) install -r requirements.txt
	@echo "$(GREEN)>>> YOLOv5配置完成！$(NC)"

download-weights: ## 下载预训练权重
	@echo "$(GREEN)>>> 下载预训练权重...$(NC)"
	@mkdir -p models/weights
	@$(PYTHON) -c "import urllib.request; urllib.request.urlretrieve('https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt', 'models/weights/yolov5s.pt')"
	@echo "$(GREEN)>>> 权重下载完成！$(NC)"

##@ 项目构建

build: install ## 构建项目（安装依赖+初始化）
	@echo "$(GREEN)>>> 构建项目...$(NC)"
	@$(PYTHON) setup.py develop
	@echo "$(GREEN)>>> 项目构建完成！$(NC)"

clean: ## 清理临时文件
	@echo "$(YELLOW)>>> 清理临时文件...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/ 2>/dev/null || true
	@echo "$(GREEN)>>> 清理完成！$(NC)"

clean-all: clean ## 深度清理（包括虚拟环境）
	@echo "$(RED)>>> 深度清理...$(NC)"
	@rm -rf $(VENV) 2>/dev/null || true
	@rm -rf results/experiments/* 2>/dev/null || true
	@echo "$(GREEN)>>> 深度清理完成！$(NC)"

##@ 运行程序

run: ## 运行主程序（交互式）
	@$(PYTHON) run.py

gui: ## 启动GUI界面
	@echo "$(GREEN)>>> 启动GUI界面...$(NC)"
	@$(PYTHON) app/main.py

##@ 训练与评估

train-baseline: ## 训练基线模型
	@echo "$(GREEN)>>> 训练基线模型...$(NC)"
	@$(PYTHON) train/train_baseline.py \
		--data data/helmet.yaml \
		--weights models/weights/yolov5s.pt \
		--epochs 100 \
		--batch-size 16

train-improved: ## 训练改进模型
	@echo "$(GREEN)>>> 训练改进模型...$(NC)"
	@$(PYTHON) train/train_improved.py \
		--data data/helmet.yaml \
		--epochs 100 \
		--batch-size 16

eval: ## 评估模型
	@echo "$(GREEN)>>> 评估模型...$(NC)"
	@$(PYTHON) evaluate/eval_model.py \
		--weights models/weights/improved_final.pt \
		--data data/helmet.yaml

compare: ## 对比基线和改进模型
	@echo "$(GREEN)>>> 对比模型性能...$(NC)"
	@$(PYTHON) evaluate/compare_models.py

##@ 测试

test: ## 运行所有测试
	@echo "$(GREEN)>>> 运行测试...$(NC)"
	@$(PYTHON) -m pytest tests/ -v

test-coverage: ## 运行测试并生成覆盖率报告
	@echo "$(GREEN)>>> 运行测试（覆盖率）...$(NC)"
	@$(PYTHON) -m pytest tests/ --cov=app --cov=models --cov-report=html
	@echo "$(GREEN)>>> 覆盖率报告: htmlcov/index.html$(NC)"

test-camera: ## 测试摄像头
	@echo "$(GREEN)>>> 测试摄像头...$(NC)"
	@$(PYTHON) -c "from app.utils.video_utils import test_camera, get_camera_list; cameras = get_camera_list(); print(f'可用摄像头: {cameras}'); test_camera(cameras[0], 5) if cameras else print('无摄像头')"

##@ 代码质量

format: ## 格式化代码
	@echo "$(GREEN)>>> 格式化代码...$(NC)"
	@$(PYTHON) -m black . --exclude="/(\.git|venv|models/yolov5)/"
	@echo "$(GREEN)>>> 代码格式化完成！$(NC)"

lint: ## 代码检查
	@echo "$(GREEN)>>> 代码检查...$(NC)"
	@$(PYTHON) -m flake8 . --exclude=venv,models/yolov5 --max-line-length=100

check: format lint ## 格式化+检查

##@ 文档

docs: ## 生成文档
	@echo "$(GREEN)>>> 生成文档...$(NC)"
	@mkdir -p docs/build
	@echo "$(YELLOW)>>> 文档功能开发中...$(NC)"

view-docs: ## 查看文档
	@echo "$(GREEN)>>> 打开文档...$(NC)"
	@$(PYTHON) -m webbrowser -t "docs/项目说明.md"

##@ 数据处理

prepare-data: ## 准备训练数据
	@echo "$(GREEN)>>> 准备训练数据...$(NC)"
	@$(PYTHON) scripts/prepare_data.py

split-data: ## 划分数据集
	@echo "$(GREEN)>>> 划分数据集...$(NC)"
	@$(PYTHON) scripts/split_dataset.py \
		--data data/raw \
		--output data/processed

augment-data: ## 数据增强
	@echo "$(GREEN)>>> 数据增强...$(NC)"
	@$(PYTHON) scripts/augment_data.py

##@ Docker（可选）

docker-build: ## 构建Docker镜像
	@echo "$(GREEN)>>> 构建Docker镜像...$(NC)"
	@docker build -t $(PROJECT_NAME):latest .

docker-run: ## 运行Docker容器
	@echo "$(GREEN)>>> 运行Docker容器...$(NC)"
	@docker run -it --rm --gpus all -v $(PWD):/workspace $(PROJECT_NAME):latest

##@ 部署

package: ## 打包项目
	@echo "$(GREEN)>>> 打包项目...$(NC)"
	@$(PYTHON) setup.py sdist bdist_wheel
	@echo "$(GREEN)>>> 打包完成: dist/$(NC)"

release: test package ## 发布（测试+打包）
	@echo "$(GREEN)>>> 准备发布...$(NC)"
	@echo "$(YELLOW)>>> 请手动上传 dist/ 目录下的文件$(NC)"

##@ 工具

tensorboard: ## 启动TensorBoard
	@echo "$(GREEN)>>> 启动TensorBoard...$(NC)"
	@tensorboard --logdir results/experiments --port 6006

jupyter: ## 启动Jupyter Notebook
	@echo "$(GREEN)>>> 启动Jupyter Notebook...$(NC)"
	@jupyter notebook notebooks/

backup: ## 备份项目
	@echo "$(GREEN)>>> 备份项目...$(NC)"
	@tar -czf backup_$(shell date +%Y%m%d_%H%M%S).tar.gz \
		--exclude=venv \
		--exclude=__pycache__ \
		--exclude=.git \
		--exclude=models/yolov5 \
		--exclude=results/experiments \
		.
	@echo "$(GREEN)>>> 备份完成！$(NC)"

##@ 信息

info: ## 显示项目信息
	@echo "$(BLUE)========================================$(NC)"
	@echo "$(GREEN)  项目信息$(NC)"
	@echo "$(BLUE)========================================$(NC)"
	@echo "项目名称: $(PROJECT_NAME)"
	@echo "Python版本: $(shell $(PYTHON) --version)"
	@echo "Pip版本: $(shell $(PIP) --version)"
	@echo "工作目录: $(shell pwd)"
	@echo "$(BLUE)========================================$(NC)"

check-env: ## 检查环境配置
	@echo "$(GREEN)>>> 检查环境配置...$(NC)"
	@$(PYTHON) -c "import sys; print(f'Python: {sys.version}')"
	@$(PYTHON) -c "import torch; print(f'PyTorch: {torch.__version__}')"
	@$(PYTHON) -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
	@$(PYTHON) -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
	@$(PYTHON) -c "from PyQt5.QtCore import QT_VERSION_STR; print(f'PyQt5: {QT_VERSION_STR}')"

##@ 快速开始

all: init install setup-yolov5 download-weights ## 一键安装所有内容
	@echo "$(GREEN)>>> 项目配置完成！$(NC)"
	@echo "$(YELLOW)>>> 运行 'make gui' 启动应用$(NC)"

demo: ## 运行演示
	@echo "$(GREEN)>>> 运行演示...$(NC)"
	@$(PYTHON) -c "print('演示功能开发中...')"










