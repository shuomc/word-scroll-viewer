import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QPushButton, QMessageBox, QMenu, QDialog, QSpinBox, QDoubleSpinBox,
    QComboBox, QFileDialog, QSlider, QGroupBox, QFormLayout
)
from PySide6.QtGui import QFont, Qt, QMouseEvent, QKeyEvent, QPalette, QColor, QAction
from PySide6.QtCore import QTimer, Property, Signal, Slot, QPoint, QSettings
from config import config

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

class SettingsDialog(QDialog):
    """设置对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setFixedSize(400, 300)
        self.setup_ui()
        self.load_settings()
        # 应用设置对话框样式
        self.setStyleSheet(config.get_settings_dialog_style())
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 字体大小设置
        font_group = QGroupBox("字体设置")
        font_layout = QFormLayout()
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(12, 100)
        self.font_size_spin.setValue(48)
        font_layout.addRow("字体大小:", self.font_size_spin)
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        # 滚动模式设置
        scroll_group = QGroupBox("滚动模式")
        scroll_layout = QFormLayout()
        
        self.scroll_mode_combo = QComboBox()
        self.scroll_mode_combo.addItems(["播完停止", "文件内循环", "下一文件"])
        self.scroll_mode_combo.setStyleSheet(config.get_combobox_style())
        scroll_layout.addRow("模式:", self.scroll_mode_combo)
        
        scroll_group.setLayout(scroll_layout)
        layout.addWidget(scroll_group)
        
        # 切换间隔设置
        interval_group = QGroupBox("切换间隔")
        interval_layout = QFormLayout()
        
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.1, 100.0)  # 0.1秒到100秒
        self.interval_spin.setValue(2.5)  # 默认2.5秒
        self.interval_spin.setSuffix(" 秒")
        self.interval_spin.setDecimals(1)  # 显示一位小数
        self.interval_spin.setSingleStep(0.1)  # 步长为0.1
        self.interval_spin.setToolTip("设置范围：0.1秒 - 100秒")
        
        interval_layout.addRow("间隔:", self.interval_spin)
        
        interval_group.setLayout(interval_layout)
        layout.addWidget(interval_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_settings(self):
        """加载设置"""
        self.font_size_spin.setValue(config.get("app", "default_font_size", 48))
        self.scroll_mode_combo.setCurrentText(config.get("app", "default_scroll_mode", "文件内循环"))
        self.interval_spin.setValue(config.get("app", "default_interval", 2.5))
    
    def save_settings(self):
        """保存设置"""
        config.set("app", "default_font_size", self.font_size_spin.value())
        config.set("app", "default_scroll_mode", self.scroll_mode_combo.currentText())
        config.set("app", "default_interval", round(self.interval_spin.value(), 1))
    
    def get_settings(self):
        """获取设置值"""
        return {
            "font_size": self.font_size_spin.value(),
            "scroll_mode": self.scroll_mode_combo.currentText(),
            "interval": round(self.interval_spin.value(), 1)
        }

class WordScrollerWindow(QWidget):
    """单词滚动显示器主窗口"""
    
    def __init__(self, word_manager):
        super().__init__()
        self.word_manager = word_manager
        self.is_locked = False  # 锁定状态
        self.setup_window()
        self.setup_ui()
        self.setup_menu()
        self.load_settings()
        self.start_word_display()
        # 设置文件切换回调
        self.word_manager.set_file_changed_callback(self.update_window_title)
        self.update_window_title()  # 注册回调后主动刷新标题，确保首次运行标题正确
    
    def setup_window(self):
        """设置窗口属性"""
        # 初始化时设置标题
        self.update_window_title()
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Window
        )
        
        # 设置窗口在屏幕中央
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_width = config.get("app", "window_width", 800)
        window_height = config.get("app", "window_height", 120)
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        self.setGeometry(x, y, window_width, window_height)
        
        # 设置背景样式
        self.setStyleSheet(config.get_main_window_style())
    
    def setup_ui(self):
        """设置用户界面"""
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
        # 添加顶部间距
        self.layout.addSpacing(10)
        
        # 单词显示标签
        self.word_label = QLabel("")
        self.word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.word_label.setStyleSheet("color: white; background-color: transparent;")
        self.layout.addWidget(self.word_label)
        
        # 解释显示标签
        self.meaning_label = QLabel("")
        self.meaning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.meaning_label.setStyleSheet("color: white; background-color: transparent; font-size: 16px;")
        self.layout.addWidget(self.meaning_label)
        
        # 初始化动画状态变量
        self._current_word_for_display = ""
        self._current_meaning_for_display = ""
        self._next_word_to_display = ""
        self._next_meaning_to_display = ""
        self._opacity = 1.0
        self.animation_state = 0  # 0: Idle, 1: Fading out, 2: Fading in
        
        # 单词切换定时器
        self.word_change_timer = QTimer(self)
        self.word_change_timer.timeout.connect(self.next_word_and_animate)
    
    def setup_menu(self):
        """设置右键菜单"""
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet(config.get_context_menu_style())
        
        # 设置选项
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)
        
        # 选择单词本选项
        select_vocab_action = QAction("选择单词本", self)
        select_vocab_action.triggered.connect(self.select_vocabulary_file)
        menu.addAction(select_vocab_action)
        
        # 导入选项
        import_action = QAction("导入", self)
        import_action.triggered.connect(self.import_files)
        menu.addAction(import_action)
        
        menu.addSeparator()
        
        # 锁定/解锁选项
        if self.is_locked:
            unlock_action = QAction("解除无边框模式", self)
            unlock_action.triggered.connect(self.unlock_window)
            menu.addAction(unlock_action)
        else:
            lock_action = QAction("无边框模式", self)
            lock_action.triggered.connect(self.lock_window)
            menu.addAction(lock_action)
        
        menu.exec(self.mapToGlobal(position))
    
    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            dialog.save_settings()
            self.word_manager.load_config()  # 新增：强制刷新配置
            self.load_settings()
            self.apply_settings()
    
    def import_files(self):
        """导入文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择要导入的文本文件",
            "",
            "文本文件 (*.txt);;所有文件 (*.*)"
        )
        
        if files:
            # 复制文件到resources目录
            resources_dir = os.path.join(get_base_dir(), "resources")
            if not os.path.exists(resources_dir):
                os.makedirs(resources_dir)

            for file_path in files:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(resources_dir, filename)

                try:
                    with open(file_path, 'r', encoding='utf-8') as src:
                        content = src.read()
                    with open(dest_path, 'w', encoding='utf-8') as dst:
                        dst.write(content)
                except Exception as e:
                    QMessageBox.warning(self, "导入失败", f"导入文件 {filename} 失败: {str(e)}")

            # 重新加载词库
            self.word_manager.load_all_vocabulary()
            QMessageBox.information(self, "导入成功", f"成功导入 {len(files)} 个文件")

    def select_vocabulary_file(self):
        """选择单词本文件"""
        # 获取当前可用的词库文件列表
        resources_dir = os.path.join(get_base_dir(), "resources")
        if not os.path.exists(resources_dir):
            QMessageBox.warning(self, "错误", "词库目录不存在")
            return

        # 获取所有txt文件
        txt_files = []
        for filename in os.listdir(resources_dir):
            if filename.endswith('.txt'):
                txt_files.append(filename)

        if not txt_files:
            QMessageBox.warning(self, "错误", "没有找到词库文件")
            return

        # 创建选择对话框
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QLabel

        dialog = QDialog(self)
        dialog.setWindowTitle("选择单词本")
        dialog.setFixedSize(400, 300)
        dialog.setStyleSheet(config.get_settings_dialog_style())

        layout = QVBoxLayout()

        # 说明标签
        label = QLabel("请选择要使用的单词本文件：")
        layout.addWidget(label)

        # 文件列表
        list_widget = QListWidget()
        list_widget.addItems(txt_files)
        # 应用白底黑字样式
        list_widget.setStyleSheet("QListWidget { background-color: white; color: black; }")
        layout.addWidget(list_widget)

        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")

        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        # 显示对话框
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_items = list_widget.selectedItems()
            if selected_items:
                selected_file = selected_items[0].text()
                # 切换到选中的文件
                self.switch_to_vocabulary_file(selected_file)

    def switch_to_vocabulary_file(self, filename):
        """切换到指定的词库文件"""
        resources_dir = os.path.join(get_base_dir(), "resources")
        file_path = os.path.join(resources_dir, filename)
        
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "错误", f"文件 {filename} 不存在")
            return
        
        # 找到文件在列表中的索引
        if hasattr(self.word_manager, 'files'):
            for i, path in enumerate(self.word_manager.files):
                if os.path.basename(path) == filename:
                    self.word_manager.current_file_index = i
                    self.word_manager.current_index = 0  # 重置到文件开头
                    self.word_manager.load_current_file()
                    self.word_manager.save_progress()
                    # 更新窗口标题
                    self.update_window_title()
                    QMessageBox.information(self, "切换成功", f"已切换到单词本：{filename}")
                    return
        
        QMessageBox.warning(self, "错误", f"无法找到文件 {filename}")
    
    def lock_window(self):
        """无边框模式"""
        self.is_locked = True
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
        )
        self.show()
        # 不弹窗

    def unlock_window(self):
        """解除无边框模式"""
        self.is_locked = False
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Window
        )
        self.show()
        # 不弹窗
    
    def load_settings(self):
        """加载设置"""
        self.font_size = config.get("app", "default_font_size", 22)
        self.scroll_mode = config.get("app", "default_scroll_mode", "下一文件")
        self.interval = config.get("app", "default_interval", 3)
    
    def apply_settings(self):
        """应用设置"""
        # 更新字体 - 原文和翻译使用相同字体
        font = QFont("Arial", self.font_size)
        self.word_label.setFont(font)
        self.meaning_label.setFont(font)
        
        # 更新切换间隔
        self.word_change_interval_ms = int(self.interval * 1000)
        if self.word_change_timer.isActive():
            self.word_change_timer.start(self.word_change_interval_ms)
    
    def update_window_title(self):
        """根据当前词库文件名更新窗口标题"""
        file_name = self.word_manager.get_current_file_name() if hasattr(self.word_manager, 'get_current_file_name') else ""
        self.setWindowTitle(f"滚动显示器  （单词本: {file_name}）")
    
    def start_word_display(self):
        """开始单词显示"""
        if not self.word_manager.load_all_vocabulary():
            self.word_label.setText("没有找到词库文件！")
            return

        self.apply_settings()  # 应用字体等设置

        # 关键：首次启动时立即显示当前单词和释义
        current_word, current_meaning = self.word_manager.get_current_word()
        self.set_current_word_text(current_word)
        self.set_current_meaning_text(current_meaning)

        # 关键：立即刷新窗口标题，确保显示正确的单词本名
        self.update_window_title()

        # 启动定时器，后续自动切换
        self.word_change_timer.start(self.word_change_interval_ms)
    
    # 属性设置
    def get_current_word_text(self):
        return self.word_label.text()
    
    def set_current_word_text(self, text):
        self.word_label.setText(text)
    
    def set_current_meaning_text(self, text):
        self.meaning_label.setText(text)
    
    current_word_text = Property(str, get_current_word_text, set_current_word_text)
    
    def get_opacity(self):
        return self._opacity
    
    def set_opacity(self, opacity):
        self._opacity = opacity
        self.word_label.setStyleSheet(f"color: white; background-color: transparent; opacity: {opacity};")
    
    opacity = Property(float, get_opacity, set_opacity)
    
    # 动画方法
    @Slot()
    def next_word_and_animate(self):
        """获取下一个单词并开始动画"""
        if not self.word_manager.is_loaded:
            return
        
        word, meaning = self.word_manager.get_current_word()
        self._next_word_to_display = word
        self._next_meaning_to_display = meaning
        self.word_manager.get_next_word()
        
        if self.animation_state == 0:
            self.animation_state = 1
            self.fade_timer = QTimer(self)
            self.fade_timer.timeout.connect(self.fade_out)
            self.fade_timer.start(50)
        # 每次单词切换都刷新标题
        self.update_window_title()
    
    def fade_out(self):
        """淡出动画"""
        current_opacity = self.opacity
        if current_opacity > 0:
            self.opacity = max(0.0, current_opacity - 0.05)
        else:
            self.fade_timer.stop()
            self.animation_state = 2
            self.set_current_word_text(self._next_word_to_display)
            self.set_current_meaning_text(self._next_meaning_to_display)
            self.fade_timer.start(50)
            self.fade_in()
    
    def fade_in(self):
        """淡入动画"""
        current_opacity = self.opacity
        if current_opacity < 1.0:
            self.opacity = min(1.0, current_opacity + 0.05)
        else:
            self.fade_timer.stop()
            self.animation_state = 0
    
    # 事件处理
    def keyPressEvent(self, event: QKeyEvent):
        """键盘事件处理"""
        if event.key() == Qt.Key.Key_Escape:
            if self.isFullScreen():
                self.toggle_fullscreen()
        event.accept()
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """双击事件处理"""
        if event.button() == Qt.MouseButton.LeftButton:
            if event.position().y() <= 30:
                self.toggle_fullscreen()
        event.accept()
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件处理"""
        if self.is_locked and event.button() == Qt.MouseButton.LeftButton:
            # 锁定状态下，左键按下开始拖动
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件处理"""
        if self.is_locked and event.buttons() & Qt.MouseButton.LeftButton:
            # 锁定状态下，左键拖动移动窗口
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def toggle_fullscreen(self):
        """切换全屏模式"""
        if self.isFullScreen():
            self.showNormal()
            self.setStyleSheet(config.get_main_window_style())
        else:
            self.showFullScreen()
            self.setStyleSheet(config.get_main_window_style())
            QMessageBox.information(self, "全屏模式", "按 Esc 键退出全屏模式") 