import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QComboBox
)
from url_utils import is_valid, detect_platform
from youtube_service import get_video_info

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MediaGrab")
        self.setMinimumSize(900, 600)

        self.video_info = None
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
        self.title_label = QLabel('Title:-')
        self.channel_label= QLabel('Channel-')
        self.duration_label = QLabel('Duration:-')
        self.quality_label = QLabel('Quality:-')
        self.quality_combo = QComboBox()
        self.quality_combo.addItem('Best')

        self.analyze_button.clicked.connect(self.analyze_url)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addSpacing(20)
        layout.addWidget(self.url_input)
        layout.addWidget(self.analyze_button)

        layout.addSpacing(10)
        layout.addWidget(self.platform)

        layout.addSpacing(20)
        layout.addWidget(self.title_label)

        layout.addWidget(self.channel_label)
        layout.addWidget(self.duration_label)   

        layout.addSpacing(10)
        layout.addWidget(self.quality_label)
        layout.addWidget(self.quality_combo)  

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
                self.video_info = get_video_info(url)

                self.display_video_info()
                
            except Exception as e:
                QMessageBox.critical(self,'Error',
                                    'Failed to retrieve video information.'
                                    f'Error: {e}')  



    def display_video_info(self):

            title = self.video_info["title"]
            channel = self.video_info["channel"]
            duration = self.video_info["duration"]

            minutes = duration // 60
            seconds = duration % 60

            self.title_label.setText(f"Title: {title}")

            self.channel_label.setText(f"Channel: {channel}")

            self.duration_label.setText(f"Duration: {minutes}:{seconds:02d}")

            self.quality_combo.clear()

            self.quality_combo.addItem("Best")

            qualities = set()

            for video_format in self.video_info["formats"]:

                height = video_format["height"]
                qualities.add(height)

            for height in sorted(qualities,reverse=True):

                self.quality_combo.addItem(f"{height}p")

