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
            f.write("Hello n.你好；\n")
            f.write("World n.世界；\n")
            f.write("Python n.蟒蛇；Python编程语言；\n")
            f.write("PySide6 n.PySide6库；\n")
            f.write("Scroll v.滚动；n.卷轴；\n")
            f.write("Word n.单词；\n")
            f.write("Example n.例子；示例；\n")
            f.write("Programming n.编程；程序设计；\n")
            f.write("Interface n.界面；接口；\n")
            f.write("Desktop n.桌面；台式机；\n")
            f.write("Application n.应用程序；应用；\n")


    main()