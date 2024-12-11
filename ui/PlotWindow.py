from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from plotly.graph_objs import FigureWidget

import ipywidgets as widgets

from src.logging.logging_config import logger

logger.info(widgets.__version__)

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotWindow(QMainWindow):
    def __init__(self, fig, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Plot Window')
        self.setGeometry(100, 100, 800, 600)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.canvas = FigureCanvas(fig)
        self.layout.addWidget(self.canvas)

    def closeEvent(self, event):
        # Close the figure when the window is closed
        plt.close(self.canvas.figure)
        event.accept()
# Example usage
# data_processor = YourDataProcessorClass()
# show_plot(data_processor, chunk_size=1000)
