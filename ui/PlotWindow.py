import webbrowser

from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QMessageBox
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from plotly.graph_objs import FigureWidget

import ipywidgets as widgets

from src.logging.logging_config import logger

logger.info(widgets.__version__)

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotWindow(QMainWindow):
    def __init__(self, fig_html, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Plot Window')
        self.setGeometry(100, 100, 800, 600)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.layout.addWidget(self.web_view)

        try:
            self.web_view.setHtml(fig_html)
            # Check if the HTML content is rendered correctly
            self.web_view.loadFinished.connect(self.check_rendering)
        except Exception as e:
            logger.error(f"Failed to render HTML in QWebEngineView: {e}")
            self.open_in_browser(fig_html)

    def check_rendering(self, success):
        if not success:
            QMessageBox.warning(self, "Rendering Issue", "Sadly, there's an issue with Qt, so we have to open the browser for now.")
            self.open_in_browser(self.web_view.page())

    def open_in_browser(self, html_content):
        # Open the HTML file in the default web browser
        webbrowser.open("fig_debug.html")

    def closeEvent(self, event):
        # Perform any cleanup if necessary
        event.accept()


