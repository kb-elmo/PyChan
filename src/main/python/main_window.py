import pyperclip

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt, QThread, QMetaObject, Q_ARG, pyqtSlot
from PyQt5 import uic

from chany import Loader
from chany import check_url


class MainWindow(QMainWindow):
    def __init__(self, ui, parent=None):
        super().__init__(parent)
        self.form = uic.loadUi(ui, self)

        self.thread = QThread()
        self.loader = Loader()

        self.form.btn_download.clicked.connect(self.start_download)
        self.form.btn_clipboard.clicked.connect(self.clipboard)

    @pyqtSlot()
    def start_download(self):
        self.form.btn_download.setText("Cancel")
        self.form.btn_download.clicked.disconnect()
        self.form.btn_download.clicked.connect(self.cancel_download)

        url = self.form.input_url.text()
        path = self.form.input_path.text()

        self.loader.finished.connect(self.download_finished)
        self.loader.status_update.connect(self.status_update)
        self.loader.info_update.connect(self.info_update)
        self.loader.progress_max.connect(self.progress_max)
        self.loader.progress_update.connect(self.progress_update)

        self.loader.moveToThread(self.thread)
        self.thread.start()

        QMetaObject.invokeMethod(self.loader, "download",
                                 Qt.QueuedConnection,
                                 Q_ARG(str, url),
                                 Q_ARG(str, path))

    @pyqtSlot()
    def download_finished(self):
        self.thread.quit()
        self.form.btn_download.setText("Download")
        self.form.btn_download.clicked.disconnect()
        self.form.btn_download.clicked.connect(self.start_download)

    @pyqtSlot()
    def cancel_download(self):
        self.loader.stop()

    @pyqtSlot(str)
    def status_update(self, status):
        self.form.status.setText(status)

    @pyqtSlot(str)
    def info_update(self, info):
        self.form.info.setText(info)

    @pyqtSlot(int)
    def progress_max(self, max_val):
        self.form.progress.setMaximum(max_val)

    @pyqtSlot(int)
    def progress_update(self, val):
        self.form.progress.setValue(val)

    @pyqtSlot()
    def clipboard(self):
        clip = pyperclip.paste()
        if check_url(clip):
            self.form.input_url.setText(clip)
