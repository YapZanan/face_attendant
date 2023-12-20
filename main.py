from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from PyQt5.QtCore import Qt, QThread

from webcam import CameraWorker


def setup_thread(worker, thread, run_method, finished_method, delete_later_method, progress_method):
    worker.moveToThread(thread)
    thread.started.connect(run_method)
    worker.finished.connect(thread.quit)
    worker.finished.connect(delete_later_method)
    thread.finished.connect(thread.deleteLater)
    worker.progress.connect(progress_method)
    thread.start()


class UI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.camera_worker = CameraWorker()
        self.camera_thread = QThread()

        uic.loadUi("123.ui", self)
        self.label_camera = self.findChild(QLabel, 'labelCamera')

        self.status_a = False
        print(self.status_a)
        setup_thread(self.camera_worker,
                     self.camera_thread,
                     self.camera_worker.run,
                     self.camera_thread.quit,
                     self.camera_worker.deleteLater,
                     self.set_label_camera)

        self.button_check_in = self.findChild(QPushButton, 'buttonCheckIn')

    def set_label_camera(self, pixmap):
        pixmap = pixmap.scaled(self.label_camera.size(), Qt.KeepAspectRatio)
        self.label_camera.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication([])
    window = UI()
    window.show()
    app.exec_()
