import os
import sys
import webbrowser
import uuid
from datetime import datetime, timedelta
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWidgets import QMessageBox, QMainWindow, QVBoxLayout, QWidget, QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
import ipywidgets as widgets
from src.logging.logging_config import logger

logger.info(widgets.__version__)

# Determine the path of the tmp_html directory
current_dir = os.path.dirname(os.path.abspath(__file__))
tmp_html_dir = os.path.join(current_dir, 'tmp_html')

# Create the tmp_html directory if it does not exist
os.makedirs(tmp_html_dir, exist_ok=True)

# variable to track if Qt rendering has failed
render_failed = False


def has_redner_failed():
    return render_failed

def cleanup_old_files(directory, days):
    now = datetime.now()
    cutoff = now - timedelta(days=days)

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_time < cutoff:
                os.remove(file_path)
                print(f"Deleted old file: {file_path}")


def open_in_browser(html_content, symbol):
    # Generate a random string for the HTML file name
    if symbol:
        plot_string = symbol
    else:
        plot_string = "example_plot"
    random_string = str(uuid.uuid4())
    html_file_path = os.path.join(tmp_html_dir, f'{plot_string}_{random_string}.html')

    # Write the HTML content to the file
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)

    # Print the path of the HTML file
    print(f"HTML file created: {html_file_path}")

    # Open the HTML file in the default web browser
    webbrowser.open(f'file://{os.path.abspath(html_file_path)}')


class PlotWindow(QMainWindow):
    def __init__(self, fig_html, symbol=None, parent=None):
        super().__init__(parent)
        self.fig_html = fig_html
        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.symbol = symbol

        # Attempt to render using Qt if render has not failed before
        if not render_failed:
            self.setWindowTitle('Plot Window')
            self.setGeometry(100, 100, 800, 600)
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            self.layout = QVBoxLayout(self.central_widget)
            self.web_view.setHtml(self.fig_html)
            self.web_view.loadFinished.connect(self.check_rendering)
            self.layout.addWidget(self.web_view)
        else:
            open_in_browser(self.fig_html, self.symbol)

    def check_rendering(self, success):
        if not success:
            QMessageBox.warning(self, "Rendering Issue",
                                "Sadly, there's an issue with Qt, so we have to open the browser for now.")
            open_in_browser(self.fig_html, self.symbol)
            global render_failed
            render_failed = True

    def closeEvent(self, event):
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Cleanup old files older than 7 days
    cleanup_old_files(tmp_html_dir, 7)

    # Example HTML content
    example_html = """
    <html>
    <head><title>Test Plot</title></head>
    <body><h1>Hello, Plot!</h1></body>
    </html>
    """

    window = PlotWindow(example_html)
    window.show()

    sys.exit(app.exec())
