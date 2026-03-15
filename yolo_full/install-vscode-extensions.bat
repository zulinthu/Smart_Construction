@echo off
chcp 65001 >nul
echo ========================================
echo  安装 VSCode 状态栏增强扩展
echo  安全帽检测系统 - YOLOv5
echo ========================================
echo.

echo [1/8] 安装 GitLens - Git增强工具...
code --install-extension eamodio.gitlens

echo [2/8] 安装 Git Graph - Git图形化...
code --install-extension mhutchie.git-graph

echo [3/8] 安装 Todo Tree - TODO追踪...
code --install-extension gruntfuggly.todo-tree

echo [4/8] 安装 VSCode Counter - 代码统计...
code --install-extension uctakeoff.vscode-counter

echo [5/8] 安装 Project Manager - 项目管理...
code --install-extension alefragnani.project-manager

echo [6/8] 安装 Error Lens - 错误提示增强...
code --install-extension usernamehw.errorlens

echo [7/8] 安装 Python 扩展...
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance

echo [8/8] 安装 vscode-icons - 文件图标...
code --install-extension vscode-icons-team.vscode-icons

echo.
echo ========================================
echo  ✓ 所有扩展安装完成！
echo ========================================
echo.
echo 请重启 VSCode 以激活所有扩展
echo 或按 Ctrl+Shift+P 输入 "Reload Window"
echo.
pause


