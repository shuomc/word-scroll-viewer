import os
import json
import sys

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

class WordManager:
    def __init__(self, config_path=None):
        base_dir = get_base_dir()
        if config_path is None:
            config_path = os.path.join(base_dir, "config.json")
        self.vocabulary = []  # 存储单词和解释的元组 [(word, meaning), ...]
        self.current_index = 0
        self.is_loaded = False
        self.current_file_index = 0
        self.files = []
        self.on_file_changed_callback = None  # 文件切换回调函数
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        return self.config

    def save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def get_config(self, section, key, default=None):
        self.load_config()
        return self.config.get(section, {}).get(key, default)

    def set_config(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()

    def load_all_vocabulary(self, resources_dir=None):
        if resources_dir is None:
            resources_dir = os.path.join(get_base_dir(), "resources")
        self.vocabulary.clear()
        self.current_index = 0
        self.is_loaded = False
        self.files = []
        if not os.path.exists(resources_dir):
            print(f"Error: Resources directory not found at {resources_dir}")
            return False
        try:
            for filename in os.listdir(resources_dir):
                if filename.endswith('.txt'):
                    file_path = os.path.join(resources_dir, filename)
                    self.files.append(file_path)
            if not self.files:
                print("No .txt files found in resources directory")
                return False
            self.load_progress()
            for file_path in self.files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                word, meaning = self.parse_word_line(line)
                                self.vocabulary.append((word, meaning))
                except Exception as e:
                    print(f"Error loading file {file_path}: {e}")
            if self.vocabulary:
                self.is_loaded = True
                print(f"Successfully loaded {len(self.vocabulary)} words from {len(self.files)} files.")
                return True
            else:
                print("No words found in any files")
                return False
        except Exception as e:
            print(f"Error loading vocabulary files: {e}")
            return False

    def load_vocabulary(self, file_path=None):
        return self.load_all_vocabulary()

    def save_progress(self):
        if self.is_loaded and self.vocabulary:
            self.set_config("app", "current_index", self.current_index)
            self.set_config("app", "current_file_index", self.current_file_index)
            self.set_config("app", "total_words", len(self.vocabulary))

    def load_progress(self):
        saved_index = self.get_config("app", "current_index", 0)
        saved_file_index = self.get_config("app", "current_file_index", 0)
        saved_total = self.get_config("app", "total_words", 0)
        if saved_total > 0:
            self.current_index = min(saved_index, saved_total - 1)
            self.current_file_index = min(saved_file_index, len(self.files) - 1) if self.files else 0
            print(f"Restored progress: word {self.current_index + 1}/{saved_total}")

    def get_current_word(self):
        if not self.is_loaded or not self.vocabulary:
            return "No words loaded", ""
        return self.vocabulary[self.current_index]

    def get_next_word(self):
        if not self.is_loaded or not self.vocabulary:
            return
        self.save_progress()
        scroll_mode = self.get_config("app", "default_scroll_mode", "文件内循环")
        if scroll_mode == "播完停止":
            if self.current_index < len(self.vocabulary) - 1:
                self.current_index += 1
            else:
                return
        elif scroll_mode == "文件内循环":
            self.current_index = (self.current_index + 1) % len(self.vocabulary)
        elif scroll_mode == "下一文件":
            self.current_index += 1
            if self.current_index >= len(self.vocabulary):
                self.current_file_index = (self.current_file_index + 1) % len(self.files)
                self.current_index = 0
                self.load_current_file()

    def load_current_file(self):
        if not self.files:
            return
        self.vocabulary.clear()
        file_path = self.files[self.current_file_index]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        word, meaning = self.parse_word_line(line)
                        self.vocabulary.append((word, meaning))
            print(f"Loaded file: {os.path.basename(file_path)} ({len(self.vocabulary)} words)")
            if self.on_file_changed_callback:
                self.on_file_changed_callback()
        except Exception as e:
            print(f"Error loading current file: {e}")

    def set_file_changed_callback(self, callback):
        self.on_file_changed_callback = callback

    def parse_word_line(self, line):
        dot_index = line.find('.')
        if dot_index == -1:
            return line.strip(), ""
        space_index = -1
        for i in range(dot_index - 1, -1, -1):
            if line[i] == ' ':
                space_index = i
                break
        if space_index == -1:
            return line.strip(), ""
        word = line[:space_index].strip()
        meaning = line[space_index + 1:].strip()
        return word, meaning

    def get_vocabulary_size(self):
        return len(self.vocabulary)

    def get_current_file_name(self):
        if self.files and self.current_file_index < len(self.files):
            return os.path.basename(self.files[self.current_file_index])
        return "Unknown"
