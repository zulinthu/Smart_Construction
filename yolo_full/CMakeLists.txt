# ========================================
# 安全帽检测系统 - CMake配置文件
# ========================================

cmake_minimum_required(VERSION 3.15)

project(helmet-detection
    VERSION 1.0.0
    DESCRIPTION "基于改进YOLOv5的安全帽检测系统"
    LANGUAGES NONE
)

# 项目配置
set(PROJECT_ROOT ${CMAKE_CURRENT_SOURCE_DIR})
set(PYTHON_EXECUTABLE python CACHE STRING "Python可执行文件")

# 输出信息
message(STATUS "========================================")
message(STATUS "  安全帽检测系统 v${PROJECT_VERSION}")
message(STATUS "========================================")
message(STATUS "项目根目录: ${PROJECT_ROOT}")
message(STATUS "Python: ${PYTHON_EXECUTABLE}")

# 自定义目标

# 1. 环境初始化
add_custom_target(init
    COMMAND ${PYTHON_EXECUTABLE} -m venv venv
    WORKING_DIRECTORY ${PROJECT_ROOT}
    COMMENT "初始化虚拟环境..."
)

# 2. 安装依赖
add_custom_target(install
    COMMAND ${PYTHON_EXECUTABLE} -m pip install --upgrade pip
    COMMAND ${PYTHON_EXECUTABLE} -m pip install -r requirements.txt
    COMMAND ${PYTHON_EXECUTABLE} config.py
    WORKING_DIRECTORY ${PROJECT_ROOT}
    COMMENT "安装项目依赖..."
)

# 3. 下载YOLOv5
add_custom_target(setup-yolov5
    COMMAND git clone https://github.com/ultralytics/yolov5.git models/yolov5
    COMMAND ${PYTHON_EXECUTABLE} -m pip install -r models/yolov5/requirements.txt
    WORKING_DIRECTORY ${PROJECT_ROOT}
    COMMENT "下载YOLOv5源码..."
)

# 4. 下载权重
add_custom_target(download-weights
    COMMAND ${CMAKE_COMMAND} -E make_directory models/weights
    COMMAND ${PYTHON_EXECUTABLE} -c "import urllib.request; urllib.request.urlretrieve('https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt', 'models/weights/yolov5s.pt')"
    WORKING_DIRECTORY ${PROJECT_ROOT}
    COMMENT "下载预训练权重..."
)

# 5. 构建项目
add_custom_target(build
    COMMAND ${PYTHON_EXECUTABLE} setup.py develop
    WORKING_DIRECTORY ${PROJECT_ROOT}
    DEPENDS install
    COMMENT "构建项目..."
)

# 6. 清理
add_custom_target(clean-temp
    COMMAND ${CMAKE_COMMAND} -E remove_directory __pycache__
    COMMAND ${CMAKE_COMMAND} -E remove *.pyc
    COMMAND ${CMAKE_COMMAND} -E remove_directory build
    COMMAND ${CMAKE_COMMAND} -E remove_directory dist
    WORKING_DIRECTORY ${PROJECT_ROOT}
    COMMENT "清理临时文件..."
)

# 7. 运行GUI
add_custom_target(gui
    COMMAND ${PYTHON_EXECUTABLE} app/main.py
    WORKING_DIRECTORY ${PROJECT_ROOT}
    COMMENT "启动GUI界面..."
)

# 8. 训练基线模型
add_custom_target(train-baseline
    COMMAND ${PYTHON_EXECUTABLE} train/train_baseline.py
        --data data/helmet.yaml
        --weights models/weights/yolov5s.pt
        --epochs 100
        --batch-size 16
    WORKING_DIRECTORY ${PROJECT_ROOT}
    COMMENT "训练基线模型..."
)

# 9. 评估模型
add_custom_target(eval
    COMMAND ${PYTHON_EXECUTABLE} evaluate/eval_model.py
        --weights models/weights/improved_final.pt
        --data data/helmet.yaml
    WORKING_DIRECTORY ${PROJECT_ROOT}
    COMMENT "评估模型..."
)

# 10. 运行测试
add_custom_target(test-all
    COMMAND ${PYTHON_EXECUTABLE} -m pytest tests/ -v
    WORKING_DIRECTORY ${PROJECT_ROOT}
    COMMENT "运行测试..."
)

# 11. 代码格式化
add_custom_target(format
    COMMAND ${PYTHON_EXECUTABLE} -m black . --exclude="/(\.git|venv|models/yolov5)/"
    WORKING_DIRECTORY ${PROJECT_ROOT}
    COMMENT "格式化代码..."
)

# 12. 代码检查
add_custom_target(lint
    COMMAND ${PYTHON_EXECUTABLE} -m flake8 . --exclude=venv,models/yolov5 --max-line-length=100
    WORKING_DIRECTORY ${PROJECT_ROOT}
    COMMENT "代码检查..."
)

# 13. TensorBoard
add_custom_target(tensorboard
    COMMAND tensorboard --logdir results/experiments --port 6006
    WORKING_DIRECTORY ${PROJECT_ROOT}
    COMMENT "启动TensorBoard..."
)

# 14. 一键安装
add_custom_target(all-install
    DEPENDS init install setup-yolov5 download-weights
    COMMENT "一键安装所有内容..."
)

# 安装规则（可选）
install(
    DIRECTORY ${PROJECT_ROOT}/
    DESTINATION ${CMAKE_INSTALL_PREFIX}
    PATTERN "venv" EXCLUDE
    PATTERN ".git" EXCLUDE
    PATTERN "__pycache__" EXCLUDE
    PATTERN "*.pyc" EXCLUDE
)

# 打包配置
set(CPACK_PACKAGE_NAME "helmet-detection")
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY ${PROJECT_DESCRIPTION})
set(CPACK_GENERATOR "ZIP;TGZ")

include(CPack)

# 输出构建信息
message(STATUS "")
message(STATUS "可用的CMake目标:")
message(STATUS "  make init              - 初始化虚拟环境")
message(STATUS "  make install           - 安装依赖")
message(STATUS "  make setup-yolov5      - 下载YOLOv5")
message(STATUS "  make download-weights  - 下载权重")
message(STATUS "  make build             - 构建项目")
message(STATUS "  make gui               - 启动GUI")
message(STATUS "  make train-baseline    - 训练基线模型")
message(STATUS "  make test-all          - 运行测试")
message(STATUS "  make all-install       - 一键安装")
message(STATUS "")
message(STATUS "使用方法:")
message(STATUS "  1. mkdir build && cd build")
message(STATUS "  2. cmake ..")
message(STATUS "  3. make [target]")
message(STATUS "========================================")










