# 单词滚动显示器 (Word Scroll Viewer)

一个基于PySide6的桌面应用程序，用于显示单词滚动效果，帮助用户学习和记忆单词。

## 功能特点

- 🎯 **单词滚动显示**：以淡入淡出效果循环显示单词
- 🖥️ **置顶窗口**：窗口始终保持在屏幕顶部中央，支持锁定模式
- 🎨 **黑色背景**：黑色背景，白色文字，清晰易读
- 🖱️ **标准窗口**：使用Windows标准窗口样式
- 📏 **内置功能**：支持拖拽移动和边缘调整大小
- 🔘 **标准按钮**：使用系统默认的最小化、最大化、关闭按钮
- 📚 **多文件支持**：读取resources目录下的所有txt文件
- 💾 **记忆功能**：记住上次阅读位置，下次启动时继续
- ⚙️ **设置功能**：右键菜单可调整字体大小、滚动模式、切换间隔
- 📁 **导入功能**：右键菜单可导入新的文本文件

## 安装和运行

### 环境要求
- Python 3.6 bn+
- PySide6

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行程序
```bash
python src/main.py
```

## 词库文件

程序会自动从 `resources/` 目录下的所有 `.txt` 文件加载单词。支持UTF-8编码。

### 词库格式
每行一个单词条目，格式为：`单词 词性.中文解释；`
例如：
```
smoke n.烟雾；v.抽烟；
apple n.苹果；
computer n.计算机；电脑；
```

程序会自动解析：
- 第一行显示：单词
- 第二行显示：词性和中文解释

### 滚动模式
- **播完停止**：播放完所有单词后停止
- **文件内循环**：在当前文件内循环播放
- **下一文件**：播放完当前文件后自动切换到下一个文件

### 记忆功能
程序会记住上次阅读的位置，下次启动时会从上次停止的地方继续。

## 项目结构

```
WordScrollViewer/
├── src/
│   ├── main.py          # 主程序入口
│   ├── gui.py           # GUI界面模块
│   ├── word_manager.py  # 单词管理器
│   ├── config.py        # 配置文件管理
│   ├── config.json      # 样式配置文件
│   └── resources/       # 词库文件目录
│       └── *.txt        # 所有txt词库文件
├── requirements.txt     # 依赖包列表
└── README.md           # 项目说明
```

## 使用说明

1. 启动程序后，窗口会出现在屏幕中央
2. 单词会每2.5秒自动切换一次，带有淡入淡出动画效果
3. 显示格式：
   - 第一行：英文单词
   - 第二行：词性和中文解释
   - 两行使用相同字体和大小
4. 窗口操作：
   - 拖拽标题栏移动窗口位置
   - 拖动窗口边缘调整大小
   - 使用标准的最小化、最大化、关闭按钮
5. 右键菜单功能：
   - 设置：调整字体大小、滚动模式、切换间隔。
   - 导入：导入新的单词本（txt 文件）。
   - 选择单词本：切换当前显示的词库文件。
   - 无边框模式/解除无边框模式：切换极简窗口显示，无弹窗打扰。

## 技术实现

- **GUI框架**：PySide6 (Qt for Python)
- **动画效果**：使用QTimer实现淡入淡出动画
- **窗口控制**：标准Windows窗口，内置拖拽和调整大小功能
- **全屏切换**：双击标题栏或按Esc键切换全屏模式
- **置顶显示**：窗口始终保持在屏幕顶部
- **词库管理**：多文件支持，自动读取resources目录下所有txt文件
- **设置管理**：使用config.json保存和恢复用户设置
- **进度记忆**：自动保存和恢复阅读进度
- **配置文件**：独立的JSON配置文件管理界面样式

## 自定义设置

### 通过界面设置
可以通过右键菜单的"设置"选项来自定义程序：

- **字体大小**：12-100像素范围内调整
- **滚动模式**：播完停止、文件内循环、下一文件
- **切换间隔**：0.1-100秒范围内调整（精确到0.1秒，默认2.5秒）

### 通过配置文件设置
可以通过修改 `config.json` 文件来自定义界面样式和默认设置：

#### 主窗口样式
```json
{
  "main_window": {
    "background_color": "black",
    "text_color": "white",
    "opacity": 1.0
  }
}
```

#### 设置对话框样式
```json
{
  "settings_dialog": {
    "background_color": "white",
    "text_color": "black",
    "button_background": "#f0f0f0",
    "button_text_color": "black"
  }
}
```

#### 右键菜单样式
```json
{
  "context_menu": {
    "background_color": "white",
    "text_color": "black",
    "selected_background": "#e6f0fa"
  }
}
```

#### 应用程序设置
```json
{
  "app": {
    "default_font_size": 22,            
    "default_interval": 2.5,
    "default_scroll_mode": "下一文件",
    "window_width": 500,
    "window_height": 120,
    "current_index": 7,
    "current_file_index": 0,
    "total_words": 26
  }
}
```

#### 下拉框设置
```json
{
  "app": {
    "background_color": "white",
    "text_color": "black"
  }
}
```

### 温馨提示：
> 修改 **config.json** 后，重启程序即可生效（部分设置可热更新）。
> 
> 颜色可用英文名、十六进制（如 `#ffffff`）、或 `rgba()` 格式。
> 
> 进度相关项（`current_index` 等）建议不要手动编辑。

### 通过代码修改
也可以通过修改代码中的以下参数来自定义程序：

- 窗口位置和大小：在 `gui.py` 的 `setup_window()` 方法中修改
- 默认设置：在 `config.py` 的 `default_config` 中修改
- 动画参数：在 `gui.py` 的动画方法中调整

## 许可证

Copyright © 2025 shuomc.

Licensed under the Apache License 2.0.