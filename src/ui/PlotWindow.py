import os
import sys
import webbrowser
import uuid
from datetime import datetime, timedelta
from PyQt6.QtCore import QUrl, QByteArray, QBuffer, QIODevice
from PyQt6.QtWidgets import QMessageBox, QMainWindow, QVBoxLayout, QWidget, QApplication
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineUrlScheme, QWebEngineUrlSchemeHandler, \
    QWebEngineUrlRequestJob
from PyQt6.QtWebEngineWidgets import QWebEngineView
import ipywidgets as widgets
from src.logging.logging_config import logger

logger.info(widgets.__version__)

# Credit for the qt render workaround goes to the original author from Stack Overflow:
# https://stackoverflow.com/questions/39184615/qwebengineview-cannot-load-large-svg-html-using-sethtml

# Determine the path of the tmp_html directory
current_dir = os.path.dirname(os.path.abspath(__file__))
tmp_html_dir = os.path.join(current_dir, '../../tmp_data/tmp_html')

# Create the tmp_html directory if it does not exist
os.makedirs(tmp_html_dir, exist_ok=True)

# Variable to track if Qt rendering has failed
render_failed = False

HTML_DATA = {}
URL_SCHEME = 'local'
TEST_FILE = 'test.data'


class UrlSchemeHandler(QWebEngineUrlSchemeHandler):
    def requestStarted(self, job):
        href = job.requestUrl().path()
        if (data := HTML_DATA.get(href)) is not None:
            if not isinstance(data, bytes):
                data = str(data).encode()
            mime = QByteArray(b'text/html')
            buffer = QBuffer(job)
            buffer.setData(data)
            buffer.open(QIODevice.OpenModeFlag.ReadOnly)
            job.reply(mime, buffer)
        else:
            print(f'ERROR: request job failed: {href!r}')
            job.fail(QWebEngineUrlRequestJob.Error.UrlNotFound)


def register_url_scheme():
    """
    Register the URL scheme handler for the custom local scheme.

    Returns:
        None
    """
    scheme = QWebEngineUrlScheme(bytes(URL_SCHEME, 'ascii'))
    scheme.setFlags(QWebEngineUrlScheme.Flag.SecureScheme |
                    QWebEngineUrlScheme.Flag.LocalScheme |
                    QWebEngineUrlScheme.Flag.LocalAccessAllowed)
    QWebEngineUrlScheme.registerScheme(scheme)


def has_render_failed():
    """
    Checks if the render has failed (global variable check).

    Returns:
        bool: True if the render has failed, False otherwise.
    """
    return render_failed


def cleanup_old_files(directory, days):
    """
    Cleanup old files by deleting older files if a certain number of days old.

    Args:
        directory (str): The directory to cleanup.
        days (int): The number of days to wait for deletion.

    Returns:
        None
    """
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
    """
    Open the HTML content in a browser.

    Args:
        html_content (str): The HTML content to be opened.
        symbol (str): The symbol for which the HTML content is to be opened.

    Returns:
        None
    """
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
        """
        PlotWindow for handling Plot window.

        Args:
            fig_html (str): The figure HTML content to be opened.
            symbol (str, optional): The symbol for which the HTML content is to be opened. Defaults to None.
            parent (QWidget, optional): The UI parent widget (not yet used). Defaults to None.
        """
        super().__init__(parent)
        self.fig_html = fig_html
        self.symbol = symbol

        # Register the URL scheme handler
        register_url_scheme()

        self.web_view = QWebEngineView()

        # Enable JavaScript
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)

        # Register the URL scheme handler
        self.web_view.page().profile().installUrlSchemeHandler(
            bytes(URL_SCHEME, 'ascii'), UrlSchemeHandler(self))

        # Attempt to render using Qt if render has not failed before
        self.setWindowTitle('Plot Window')
        self.setGeometry(100, 100, 800, 600)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Check if the symbol is provided and prepare HTML content
        HTML_DATA[TEST_FILE] = self.fig_html

        url = QUrl(TEST_FILE)
        url.setScheme(URL_SCHEME)
        self.web_view.setUrl(url)

        self.web_view.loadFinished.connect(self.check_rendering)
        self.layout.addWidget(self.web_view)

    def check_rendering(self, success):
        """
        Checks if the HTML content is rendering correctly and, if not, opens a browser window.

        Args:
            success (bool): The flag indicating if rendering was successful.

        Returns:
            None
        """
        global render_failed
        if not success:
            logger.error("Qt rendering failed. Falling back to browser.")
            QMessageBox.warning(self, "Rendering Issue",
                                "Sadly, there's an issue with Qt, so we have to open the browser for now.")
            open_in_browser(self.fig_html, self.symbol)
            render_failed = True
        else:
            logger.info("Qt rendering succeeded.")

    def closeEvent(self, event):
        """
        Handle close event.

        Args:
            event (QCloseEvent): The close event.

        Returns:
            None
        """
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


