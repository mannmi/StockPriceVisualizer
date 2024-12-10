from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QMenuBar, QMenu
from PyQt6.QtGui import QAction
from ui_docker_config_widget import DockerConfigWidget
from appDemo import AppDemo

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Docker Container Config')
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.docker_config_widget = DockerConfigWidget()
        self.app_demo_widget = AppDemo()

        self.create_menus()

    def create_menus(self):
        menubar = self.menuBar()

        # Create Docker Config menu
        docker_menu = menubar.addMenu('Docker Config')
        docker_action = QAction('Show Docker Config', self)
        docker_action.triggered.connect(self.show_docker_config)
        docker_menu.addAction(docker_action)

        # Create App Demo menu
        app_demo_menu = menubar.addMenu('App Demo')
        app_demo_action = QAction('Show App Demo', self)
        app_demo_action.triggered.connect(self.show_app_demo)
        app_demo_menu.addAction(app_demo_action)

    def show_docker_config(self):
        self.layout.addWidget(self.docker_config_widget)
        self.docker_config_widget.show()
        self.app_demo_widget.hide()

    def show_app_demo(self):
        self.layout.addWidget(self.app_demo_widget)
        self.app_demo_widget.show()
        self.docker_config_widget.hide()

if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())