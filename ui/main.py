import sys
from PyQt6.QtWidgets import QApplication
from ui_main_window import MainWindow

if __name__ == "__main__":
    print("yes")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())