import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox
)
from url_utils import is_valid, detect_platform
from youtube_service import get_video_info

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MediaGrab")
        self.setMinimumSize(900, 600)

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        title = QLabel("MediaGrab")
        title.setStyleSheet("font-size: 32px; font-weight: bold;")

        subtitle = QLabel("Download media from supported platforms")

        self.url_input = QLineEdit()
        self.url_input.returnPressed.connect(self.analyze_url)
        self.url_input.setPlaceholderText("Paste a video URL here...")

        self.analyze_button = QPushButton("Analyze URL")

        self.platform = QLabel('Platform - ')

        self.analyze_button.clicked.connect(self.analyze_url)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        layout.addWidget(self.url_input)
        layout.addWidget(self.analyze_button)
        layout.addWidget(self.platform)
        layout.addStretch()

    def analyze_url(self):
        url = self.url_input.text().strip()

        if not is_valid(url):

            QMessageBox.warning(self,'Invalid URL','Please enter valid URL')
            return

        platform = detect_platform(url)

        if platform == "Unknown":
            QMessageBox.warning(self,'Unsupported Platform','The provided URL is from an unsupported platform.')
            return
        
        self.platform.setText(f'Platform - {platform}')

        if platform == "YouTube":
            try:
                info=get_video_info(url)

                title = info.get('title','Unknown Title')
                channel = info.get('channel','Unknown Channel')
                duration = info.get('duration',0)

                min = duration // 60
                sec = duration % 60

                QMessageBox.information(self,'Video Info',
                                        f'Title: {title}\n'
                                        f'Channel: {channel}\n'
                                        f'Duration: {min}m {sec}s')

            except Exception as e:
                QMessageBox.critical(self,'Error',
                                    'Failed to retrieve video information.'
                                    f'Error: {e}')  

