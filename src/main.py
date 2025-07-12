import sys
import os
from PySide6.QtWidgets import QApplication
from word_manager import WordManager
from gui import WordScrollerWindow

def main():
    app = QApplication(sys.argv)
    word_manager = WordManager()
    window = WordScrollerWindow(word_manager)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    # 确保resources目录存在
    if not os.path.exists("../resources"):
        os.makedirs("../resources")

    # 如果resources目录为空，创建示例文件
    if not os.listdir("../resources"):
        with open("../resources/words.txt", "w", encoding="utf-8") as f:
            f.write("Hello\n")
            f.write("World\n")
            f.write("Python\n")
            f.write("PySide6\n")
            f.write("Scroll\n")
            f.write("Word\n")
            f.write("Example\n")
            f.write("Programming\n")
            f.write("Interface\n")
            f.write("Desktop\n")
            f.write("Application\n")
    
    main()