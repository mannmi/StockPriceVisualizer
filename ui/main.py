import sys
from PyQt6.QtWidgets import QApplication

from src.logging.logging_config import logger
from ui.appDemo import AppDemo

if __name__ == "__main__":
    logger.info("yes")
    app = QApplication(sys.argv)
    window = AppDemo()
    window.show()
    sys.exit(app.exec())