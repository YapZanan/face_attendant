import time

import face_recognition
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal, QThread
from PyQt5.QtGui import QImage, QPixmap

import cv2


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self):
        """Long-running task."""
        for i in range(100):
            self.progress.emit(i + 1)
            QThread.msleep(1000)  # Simulate a time-consuming operation
        self.finished.emit()


class CameraWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(QPixmap)

    def run(self):
        cap = cv2.VideoCapture(0)
        face_locations = []
        print("aa")

        while True:
            ret, frame = cap.read()
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            if ret:
                # Find all face locations in the current frame
                face_locations = face_recognition.face_locations(small_frame)

                # Blur faces in the frame
                self.blur_faces(small_frame, face_locations)

                # Rescale small_frame back to the original size
                frame = cv2.resize(small_frame, (frame.shape[1], frame.shape[0]))

                pixmap = self.frame_to_pixmap(frame)
                self.progress.emit(pixmap)

    def blur_faces(self, frame, face_locations):
        for face_location in face_locations:
            top, right, bottom, left = face_location

            # Extract the region of interest (face)
            face = frame[top:bottom, left:right]

            # Apply a blur effect to the face
            face = cv2.GaussianBlur(face, (99, 99), 30)

            # Replace the original face with the blurred face in the frame
            frame[top:bottom, left:right] = face

    def frame_to_pixmap(self, frame):
        pixmap = QPixmap.fromImage(QImage(frame.data, frame.shape[1], frame.shape[0],
                                          frame.strides[0], QImage.Format_RGB888).rgbSwapped())
        return pixmap


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

        self.worker = Worker()
        self.worker_thread = QThread()

        uic.loadUi("123.ui", self)
        self.label_camera = self.findChild(QLabel, 'labelCamera')
        self.button_buka_kamera = self.findChild(QPushButton, 'buttonBukaKamera')
        self.button_buka_kamera.clicked.connect(lambda: setup_thread(self.camera_worker,
                                                                     self.camera_thread,
                                                                     self.camera_worker.run,
                                                                     self.camera_thread.quit,
                                                                     self.camera_worker.deleteLater,
                                                                     self.set_label_camera))

        self.button_check_in = self.findChild(QPushButton, 'buttonCheckIn')


    def set_label_camera(self, pixmap):
        # Resize the image to fit the label without cropping
        pixmap = pixmap.scaled(self.label_camera.size(), Qt.KeepAspectRatio)

        # Update the QLabel with the resized QPixmap
        self.label_camera.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication([])
    window = UI()
    window.show()
    app.exec_()
