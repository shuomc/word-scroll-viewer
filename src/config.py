import json
import os
import sys
from pathlib import Path

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

class Config:
    def __init__(self):
        base_dir = get_base_dir()
        self.config_file = Path(os.path.join(base_dir, "config.json"))
        self.default_config = {
            "main_window": {
                "background_color": "black",
                "text_color": "white",
                "opacity": 1.0
            },
            "settings_dialog": {
                "background_color": "white",
                "text_color": "black",
                "button_background": "#f0f0f0",
                "button_text_color": "black"
            },
            "context_menu": {
                "background_color": "white",
                "text_color": "black",
                "selected_background": "#e6f0fa"
            },
            "app": {
                "default_font_size": 22,
                "default_interval": 2.5,
                "default_scroll_mode": "下一文件",
                "window_width": 500,
                "window_height": 120,
                "current_index": 7,
                "current_file_index": 0,
                "total_words": 26
            },
            "combobox": {
                "background_color": "white",
                "text_color": "black"
            }
        }
        self.load_config()

    def load_config(self):
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self._merge_config(self.default_config, self.config)
            else:
                self.config = self.default_config.copy()
                self.save_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self.config = self.default_config.copy()

    def save_config(self):
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")

    def _merge_config(self, default, current):
        for key, value in default.items():
            if key not in current:
                current[key] = value
            elif isinstance(value, dict) and isinstance(current[key], dict):
                self._merge_config(value, current[key])

    def get(self, section, key, default=None):
        try:
            return self.config[section][key]
        except KeyError:
            return default

    def set(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()

    def get_main_window_style(self):
        bg_color = self.get("main_window", "background_color", "black")
        text_color = self.get("main_window", "text_color", "white")
        return f"""
            QWidget {{
                background-color: {bg_color};
                color: {text_color};
            }}
            QMainWindow {{
                background-color: {bg_color};
                color: {text_color};
            }}
        """

    def get_settings_dialog_style(self):
        bg_color = self.get("settings_dialog", "background_color", "white")
        text_color = self.get("settings_dialog", "text_color", "black")
        button_bg = self.get("settings_dialog", "button_background", "#f0f0f0")
        button_text = self.get("settings_dialog", "button_text_color", "black")
        return f"""
            QDialog {{
                background-color: {bg_color};
                color: {text_color};
            }}
            QGroupBox {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {text_color};
            }}
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
            }}
            QPushButton {{
                background-color: {button_bg};
                color: {button_text};
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px 15px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QDoubleSpinBox, QSpinBox {{
                background-color: white;
                color: black;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 3px;
            }}
        """

    def get_context_menu_style(self):
        bg_color = self.get("context_menu", "background_color", "white")
        text_color = self.get("context_menu", "text_color", "black")
        selected_bg = self.get("context_menu", "selected_background", "#e6f0fa")
        return f"""
            QMenu {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid #cccccc;
            }}
            QMenu::item:selected {{
                background-color: {selected_bg};
            }}
        """

    def get_combobox_style(self):
        bg_color = self.get("combobox", "background_color", "white")
        text_color = self.get("combobox", "text_color", "black")
        return f"""
            QComboBox {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 3px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {bg_color};
                color: {text_color};
                selection-background-color: #e6f0fa;
                selection-color: {text_color};
            }}
        """

# 全局配置实例
config = Config() 