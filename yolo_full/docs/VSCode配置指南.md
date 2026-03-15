# VSCode配置指南

## 🎯 概述

本项目已完整配置VSCode开发环境，包括：
- ✅ 任务系统（Tasks）
- ✅ 调试配置（Launch）
- ✅ 项目设置（Settings）
- ✅ 推荐扩展（Extensions）
- ✅ 快捷键（Keybindings）

---

## 🚀 快速开始

### 1. 安装推荐扩展

打开VSCode后，会自动提示安装推荐的扩展。点击"安装所有"即可。

或者手动安装：
1. 按 `Ctrl+Shift+X` 打开扩展面板
2. 搜索并安装以下扩展：
   - Python
   - Pylance
   - Black Formatter
   - Jupyter
   - GitLens

### 2. 使用任务系统

#### 方法1：通过菜单
1. 按 `Ctrl+Shift+P` 打开命令面板
2. 输入 "Tasks: Run Task"
3. 选择要执行的任务

#### 方法2：使用快捷键
- `Ctrl+Shift+B` - 运行默认构建任务（启动GUI）
- `Ctrl+Shift+R` - 启动GUI应用
- `Ctrl+Shift+T` - 运行测试

#### 方法3：底部状态栏
点击底部状态栏的任务图标，快速选择任务。

---

## 📋 可用任务列表

### 🚀 主要任务

| 任务名称 | 说明 | 快捷键 |
|---------|------|--------|
| ▶️ 启动GUI应用 | 启动图形界面 | `Ctrl+Shift+R` |
| 🚀 一键安装所有依赖 | 安装所有必需组件 | - |
| 📦 安装依赖 | 仅安装Python依赖 | - |

### 🏋️ 训练与评估

| 任务名称 | 说明 |
|---------|------|
| 🏋️ 训练基线模型 | 训练YOLOv5基线模型 |
| 📊 评估模型 | 评估模型性能 |
| 📈 启动TensorBoard | 查看训练日志 |

### 🧪 测试

| 任务名称 | 说明 | 快捷键 |
|---------|------|--------|
| 🧪 运行测试 | 运行所有测试 | `Ctrl+Shift+T` |
| 📹 测试摄像头 | 测试摄像头功能 | - |

### 🎨 代码质量

| 任务名称 | 说明 | 快捷键 |
|---------|------|--------|
| 🎨 格式化代码 | 使用Black格式化 | `Ctrl+Shift+F` |
| 🔍 代码检查 | 使用Flake8检查 | `Ctrl+Shift+L` |

### 🛠️ 工具

| 任务名称 | 说明 | 快捷键 |
|---------|------|--------|
| 🧹 清理临时文件 | 清理缓存文件 | `Ctrl+Shift+C` |
| ℹ️ 检查环境 | 检查环境配置 | `Ctrl+Shift+E` |

---

## 🐛 调试配置

### 启动调试

1. 按 `F5` 或点击左侧调试图标
2. 选择调试配置：
   - ▶️ 启动GUI应用
   - 🏋️ 训练基线模型
   - 📊 评估模型
   - 🧪 运行测试
   - 🐛 调试当前文件

### 调试快捷键

| 快捷键 | 功能 |
|--------|------|
| `F5` | 开始调试 |
| `F9` | 设置断点 |
| `F10` | 单步跳过 |
| `F11` | 单步进入 |
| `Shift+F11` | 单步跳出 |
| `Shift+F5` | 停止调试 |

---

## ⚙️ 项目设置说明

### Python配置

```json
"python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe"
```
- 自动使用项目虚拟环境

### 格式化配置

```json
"editor.formatOnSave": true
```
- 保存时自动格式化代码
- 使用Black格式化器
- 行长度限制：100

### Linting配置

```json
"python.linting.flake8Enabled": true
```
- 启用Flake8代码检查
- 最大行长度：100
- 忽略某些规则（E203, W503）

### 测试配置

```json
"python.testing.pytestEnabled": true
```
- 使用pytest进行测试
- 自动发现测试文件

---

## ⌨️ 快捷键大全

### 任务相关

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Shift+B` | 运行默认构建任务 |
| `Ctrl+Shift+P` → "Tasks" | 打开任务菜单 |
| `Ctrl+Shift+R` | 启动GUI应用 |
| `Ctrl+Shift+T` | 运行测试 |
| `Ctrl+Shift+F` | 格式化代码 |
| `Ctrl+Shift+L` | 代码检查 |
| `Ctrl+Shift+C` | 清理临时文件 |
| `Ctrl+Shift+E` | 检查环境 |

### 编辑相关

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+/` | 注释/取消注释 |
| `Alt+↑/↓` | 移动行 |
| `Ctrl+D` | 选择下一个相同的词 |
| `Ctrl+Shift+K` | 删除行 |
| `Ctrl+Enter` | 在下方插入行 |
| `Ctrl+Shift+Enter` | 在上方插入行 |

### 导航相关

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+P` | 快速打开文件 |
| `Ctrl+Shift+O` | 跳转到符号 |
| `F12` | 跳转到定义 |
| `Alt+F12` | 查看定义 |
| `Ctrl+G` | 跳转到行 |
| `Ctrl+Tab` | 切换文件 |

### 终端相关

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+\`` | 打开/关闭终端 |
| `Ctrl+Shift+\`` | 新建终端 |
| `Ctrl+Shift+5` | 拆分终端 |

---

## 🎨 状态栏按钮

VSCode底部状态栏会显示：

1. **Python解释器** - 点击可切换虚拟环境
2. **Git分支** - 显示当前分支
3. **错误和警告** - 点击查看问题面板
4. **测试状态** - 点击运行测试
5. **格式化** - 点击格式化当前文件

---

## 🔧 自定义配置

### 添加新任务

编辑 `.vscode/tasks.json`：

```json
{
    "label": "我的任务",
    "type": "shell",
    "command": "python my_script.py",
    "group": "build",
    "presentation": {
        "reveal": "always"
    }
}
```

### 添加新快捷键

编辑 `.vscode/keybindings.json`：

```json
{
    "key": "ctrl+shift+m",
    "command": "workbench.action.tasks.runTask",
    "args": "我的任务"
}
```

### 修改设置

按 `Ctrl+,` 打开设置，搜索并修改：
- Python解释器路径
- 格式化选项
- Linting规则
- 等等...

---

## 📦 推荐扩展详解

### 必装扩展

#### 1. Python (ms-python.python)
- Python语言支持
- IntelliSense代码补全
- 调试功能

#### 2. Pylance (ms-python.vscode-pylance)
- 快速、功能丰富的语言服务器
- 类型检查
- 自动导入

#### 3. Black Formatter
- Python代码格式化
- PEP 8兼容

#### 4. Jupyter
- Jupyter Notebook支持
- 交互式Python开发

### 增强扩展

#### 5. GitLens
- Git功能增强
- 代码历史追踪
- 责任归属

#### 6. autoDocstring
- 自动生成文档字符串
- 支持多种格式

#### 7. Better Comments
- 彩色注释
- TODO高亮

#### 8. Markdown All in One
- Markdown编辑增强
- 目录生成
- 预览

---

## 🎯 使用技巧

### 技巧1：快速启动GUI
```
按 Ctrl+Shift+R 或 F5
```

### 技巧2：边开发边测试
```
1. 在编辑器中打开测试文件
2. 点击函数旁的"Run Test"按钮
3. 查看测试结果
```

### 技巧3：多终端工作
```
1. Ctrl+Shift+` 打开新终端
2. 一个终端运行GUI
3. 另一个终端运行TensorBoard
4. 第三个终端用于Git操作
```

### 技巧4：使用代码片段
```
输入 "def" 然后按 Tab
自动生成函数模板和文档字符串
```

### 技巧5：快速导航
```
Ctrl+P 输入文件名快速打开
Ctrl+Shift+O 查看当前文件的所有函数/类
F12 跳转到定义
```

---

## 🐛 常见问题

### Q1：虚拟环境未激活

**解决方案：**
1. 按 `Ctrl+Shift+P`
2. 输入 "Python: Select Interpreter"
3. 选择 `./venv/Scripts/python.exe`

### Q2：任务无法运行

**解决方案：**
```bash
# 确保构建脚本有执行权限
chmod +x build.sh  # Linux/Mac

# 或使用Python脚本
python build.py gui
```

### Q3：格式化不工作

**解决方案：**
```bash
# 安装Black
pip install black

# 重启VSCode
```

### Q4：测试发现失败

**解决方案：**
```bash
# 安装pytest
pip install pytest

# 配置测试路径
# 在settings.json中检查python.testing.pytestArgs
```

### Q5：终端找不到命令

**解决方案：**
```bash
# 激活虚拟环境
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

---

## 📚 扩展阅读

### VSCode官方文档
- [Python in VSCode](https://code.visualstudio.com/docs/languages/python)
- [Debugging](https://code.visualstudio.com/docs/editor/debugging)
- [Tasks](https://code.visualstudio.com/docs/editor/tasks)

### 项目相关文档
- [构建系统使用指南](构建系统使用指南.md)
- [快速开始](快速开始.md)
- [项目说明](项目说明.md)

---

## 💡 最佳实践

1. **使用虚拟环境**
   - 始终在项目虚拟环境中工作
   - 避免全局安装包

2. **保存时格式化**
   - 启用 `editor.formatOnSave`
   - 保持代码风格一致

3. **使用调试器**
   - 不要只用print调试
   - 学会设置断点和查看变量

4. **定期运行测试**
   - 使用 `Ctrl+Shift+T` 快速测试
   - 保持测试通过

5. **利用快捷键**
   - 提高开发效率
   - 减少鼠标使用

---

## 🎉 总结

VSCode配置已完成！现在您可以：

✅ 一键启动GUI应用（`Ctrl+Shift+R`）
✅ 快速运行测试（`Ctrl+Shift+T`）
✅ 自动格式化代码（保存时）
✅ 智能代码补全和跳转
✅ 强大的调试功能
✅ 完整的任务系统

**开始使用：**
1. 按 `Ctrl+Shift+P` 打开命令面板
2. 输入 "Tasks: Run Task"
3. 选择 "▶️ 启动GUI应用"

或直接按 `Ctrl+Shift+R`！

**Happy Coding! 🚀**










