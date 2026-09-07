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
    QComboBox,
    QProgressBar,
    QFrame,
    QHBoxLayout
)

from PySide6.QtCore import QThread

from download_worker import DownloadWorker
from url_utils import is_valid, detect_platform
from youtube_service import get_video_info

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MediaGrab")
        self.setMinimumSize(760, 580)

        self.video_info = None
        self.setup_ui()

#------------------------------------------------------------------------------------

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(52, 42, 52, 36)
        layout.setSpacing(14)

        title = QLabel("MediaGrab")
        title.setObjectName("title")

        subtitle = QLabel("Paste a link, choose a quality, and save your media in a few clicks.")
        subtitle.setObjectName("subtitle")

        self.url_input = QLineEdit()
        self.url_input.returnPressed.connect(self.analyze_url)
        self.url_input.setPlaceholderText("Paste a video URL here...")

        self.analyze_button = QPushButton("Analyze URL")
        self.analyze_button.setObjectName("primaryButton")

        self.platform = QLabel('Waiting for a link')
        self.platform.setObjectName("platformBadge")
        self.title_label = QLabel('Title will appear here')
        self.title_label.setObjectName("mediaTitle")
        self.channel_label= QLabel('Channel —')
        self.duration_label = QLabel('Duration —')
        self.quality_label = QLabel('Download quality')
        self.quality_combo = QComboBox()
        self.quality_combo.addItem('Best')

        self.download_button = QPushButton('Download media')
        self.download_button.setObjectName("downloadButton")

        self.download_button.setEnabled(False)
        self.download_button.clicked.connect(self.start_download)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)

        self.analyze_button.clicked.connect(self.analyze_url)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addSpacing(16)
        url_row = QHBoxLayout()
        url_row.setSpacing(10)
        url_row.addWidget(self.url_input, 1)
        url_row.addWidget(self.analyze_button)
        layout.addLayout(url_row)

        details_card = QFrame()
        details_card.setObjectName("detailsCard")
        details_layout = QVBoxLayout(details_card)
        details_layout.setContentsMargins(22, 20, 22, 20)
        details_layout.setSpacing(10)
        details_layout.addWidget(self.platform)
        details_layout.addWidget(self.title_label)
        details_layout.addWidget(self.channel_label)
        details_layout.addWidget(self.duration_label)
        layout.addWidget(details_card)

        layout.addSpacing(4)
        layout.addWidget(self.quality_label)
        layout.addWidget(self.quality_combo)

        layout.addSpacing(12)
        layout.addWidget(self.download_button)  

        layout.addWidget(self.progress_bar)

        layout.addStretch()

        self.setStyleSheet("""
            QMainWindow { background: #101827; }
            QWidget { color: #dce6f5; font-family: 'Segoe UI'; font-size: 14px; }
            QLabel#title { color: #f8fafc; font-size: 34px; font-weight: 700; }
            QLabel#subtitle { color: #94a3b8; font-size: 15px; }
            QLineEdit, QComboBox {
                background: #1e293b; border: 1px solid #334155; border-radius: 9px;
                padding: 11px 13px; color: #f8fafc; min-height: 22px;
            }
            QLineEdit:focus, QComboBox:focus { border: 1px solid #38bdf8; }
            QPushButton { border: 0; border-radius: 9px; padding: 11px 18px; font-weight: 600; }
            QPushButton#primaryButton { background: #0ea5e9; color: #ffffff; }
            QPushButton#primaryButton:hover { background: #38bdf8; }
            QPushButton#downloadButton { background: #22c55e; color: #062b16; }
            QPushButton#downloadButton:hover { background: #4ade80; }
            QPushButton:disabled { background: #334155; color: #94a3b8; }
            QFrame#detailsCard { background: #172235; border: 1px solid #27364c; border-radius: 12px; }
            QLabel#platformBadge { color: #7dd3fc; font-weight: 700; }
            QLabel#mediaTitle { color: #f8fafc; font-size: 17px; font-weight: 600; }
            QProgressBar { border: 0; border-radius: 5px; background: #1e293b; height: 10px; text-align: center; }
            QProgressBar::chunk { background: #0ea5e9; border-radius: 5px; }
            QStatusBar { color: #94a3b8; }
        """)

#------------------------------------------------------------------------------------

    def analyze_url(self):
        url = self.url_input.text().strip()

        if not is_valid(url):

            QMessageBox.warning(self,'Invalid URL','Please enter valid URL')
            return

        platform = detect_platform(url)

        if platform == "Unknown":
            QMessageBox.warning(self,'Unsupported Platform','The provided URL is from an unsupported platform.')
            return
        
        self.platform.setText(f'{platform} link detected')

        if platform == "YouTube":
            try:
                self.video_info = get_video_info(url)

                self.display_video_info()
                
            except Exception as e:
                QMessageBox.critical(self,'Error',
                                    'Failed to retrieve video information.'
                                    f'Error: {e}')  

#------------------------------------------------------------------------------------

    def display_video_info(self):

            title = self.video_info["title"]
            channel = self.video_info["channel"]
            duration = self.video_info["duration"]

            minutes = duration // 60
            seconds = duration % 60

            self.title_label.setText(title)
            self.channel_label.setText(f"Channel · {channel}")
            self.duration_label.setText(f"Duration · {minutes}:{seconds:02d}")

            self.quality_combo.clear()
            self.quality_combo.addItem("Best")

            qualities = set()

            for video_format in self.video_info["formats"]:

                height = video_format["height"]
                qualities.add(height)

            for height in sorted(qualities,reverse=True):

                self.quality_combo.addItem(f"{height}p")

            self.download_button.setEnabled(True)

#------------------------------------------------------------------------------------

    def start_download(self):

        url = self.url_input.text().strip()

        if not url:
            return

        self.download_button.setEnabled(False)
        self.analyze_button.setEnabled(False)

        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

        self.thread = QThread()

        quality = self.quality_combo.currentText()

        self.worker = DownloadWorker(url,"downloads",quality)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.download)

        self.worker.progress.connect(self.update_progress)

        self.worker.finished.connect(self.download_finished)

        self.worker.error.connect(self.download_error)

        self.thread.start()

#------------------------------------------------------------------------------------

    def update_progress(self, percentage):
        self.progress_bar.setValue(int(percentage))

#------------------------------------------------------------------------------------

    def download_finished(self):

        self.progress_bar.setValue(100)

        self.download_button.setEnabled(True)
        self.analyze_button.setEnabled(True)

        self.statusBar().showMessage("Download completed.")

        self.thread.quit()
        self.thread.wait()

        QMessageBox.information(
            self,
            "Download Complete",
            "Video downloaded successfully."
        )

#------------------------------------------------------------------------------------
   
    def download_error(self, message):

        self.download_button.setEnabled(True)
        self.analyze_button.setEnabled(True)

        self.progress_bar.setVisible(False)

        self.statusBar().showMessage("Download failed.")

        self.thread.quit()
        self.thread.wait()

        QMessageBox.critical(
            self,
            "Download Error",
            message
        )

#------------------------------------------------------------------------------------
