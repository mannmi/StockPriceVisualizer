import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Interactive Graph")

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.update_plot()

        toolbar = NavigationToolbar(self.canvas, self)

        button = QPushButton("Update Graph")
        button.clicked.connect(self.update_plot)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_plot(self):
        x = [i for i in range(10)]
        y = [random.randint(0, 10) for _ in range(10)]

        self.canvas.axes.cla()
        self.canvas.axes.plot(x, y, marker='o')
        self.canvas.draw()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()