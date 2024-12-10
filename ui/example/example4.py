import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objs as go
import plotly.io as pio

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Interactive Graph with Plotly")

        # Create a Plotly figure
        self.fig = go.Figure()

        # Add scatter plot to the figure
        self.fig.add_trace(go.Scatter(x=[1, 2, 3, 4, 5], y=[10, 11, 12, 13, 14], mode='lines+markers'))

        # Set layout for the figure
        self.fig.update_layout(title='Interactive Plotly Graph', xaxis_title='X Axis', yaxis_title='Y Axis')

        # Convert Plotly figure to HTML
        self.html = pio.to_html(self.fig, full_html=False)

        # Create a QWebEngineView and set the HTML content
        self.browser = QWebEngineView()
        self.browser.setHtml(self.html)

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
