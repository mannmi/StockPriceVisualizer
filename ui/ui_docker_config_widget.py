from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel

class DockerConfigWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.ip_label = QLabel('Docker Container IP:')
        self.layout.addWidget(self.ip_label)

        self.ip_input = QLineEdit(self)
        self.layout.addWidget(self.ip_input)

        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        self.layout.addWidget(self.output)

        self.btn_add_ip = QPushButton('Add IP', self)
        self.btn_add_ip.clicked.connect(self.add_ip)
        self.layout.addWidget(self.btn_add_ip)

        self.setLayout(self.layout)

    def add_ip(self):
        ip_address = self.ip_input.text()
        # Here you would add the logic to handle the IP address for the Docker container
        self.output.append(f"Added IP: {ip_address}")