import yt_dlp
from PySide6.QtCore import QObject, Signal


class DownloadWorker(QObject):

    progress = Signal(float)
    finished = Signal()
    error = Signal(str)

    def __init__(self, url, output_path,quality):
        super().__init__()

        self.url = url
        self.output_path = output_path
        self.quality = quality

    def download(self):

        try:

            if self.quality == "Best":
                format_selector = ("bestvideo+bestaudio/best")

            else:
                height = int(self.quality.replace("p", ""))

                format_selector = (
                    f"bestvideo[height<={height}]"
                    f"+bestaudio/"
                    f"best[height<={height}]"
                )

            print(format_selector)
            
            options = {
                "format": format_selector,
                "merge_output_format": "mp4",
                "outtmpl": f"{self.output_path}/%(title)s.%(ext)s",
                #"quiet": True,
                #"no_warnings": True,
                "progress_hooks": [self.progress_hook]
            }

            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([self.url])

            self.finished.emit()

        except Exception as error:
            self.error.emit(str(error))

    def progress_hook(self, data):

        if data["status"] == "downloading":

            downloaded = data.get("downloaded_bytes",0)
            total = data.get("total_bytes")

            if total:
                percentage = (downloaded / total) * 100
                self.progress.emit(percentage)