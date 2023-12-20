import os
from datetime import datetime

import cv2
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, QThread

from webcam import CameraWorker
import csv


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
        self.setup_camera_thread()

        self.button_check_in = self.findChild(QPushButton, 'buttonCheckIn')
        self.button_check_in.clicked.connect(self.check_in)

        self.button_check_out = self.findChild(QPushButton, 'buttonCheckOut')
        self.button_check_out.clicked.connect(self.check_out)

    def setup_camera_thread(self):
        self.label_camera = self.findChild(QLabel, 'labelCamera')
        setup_thread(self.camera_worker,
                     self.camera_thread,
                     self.camera_worker.run,
                     self.camera_thread.quit,
                     self.camera_worker.deleteLater,
                     self.set_label_camera)

    def set_label_camera(self, pixmap):
        pixmap = pixmap.scaled(self.label_camera.size(), Qt.KeepAspectRatio)
        self.label_camera.setPixmap(pixmap)

    def process_frame_and_show_message(self, check_type):
        current_frame = self.camera_worker.current_frame
        face_locations, face_names, number_id = self.camera_worker.process_frame(current_frame)
        print(self.camera_worker.process_frame(current_frame))

        if face_names:
            first_face_name = face_names[0]
            id = number_id[0]

            if first_face_name != "Unknown":
                if not self.already_checked(id, check_type):
                    self.save_image(current_frame, first_face_name, id)
                    self.save_to_csv(first_face_name, id, check_type)
                    message = f"{first_face_name} berhasil {check_type}!"
                    success_message = QMessageBox.Information
                else:
                    message = f"Anda sudah {check_type} hari ini"
                    success_message = QMessageBox.Warning

                self.show_unknown_message(success_message, message, "Warning" if success_message == QMessageBox.Warning else "Success")
                if success_message == QMessageBox.Warning:
                    print(f"You have already {check_type.lower()} today.")
            else:
                print("No Face Detected")
                self.show_unknown_message(QMessageBox.Warning, "Wajah tidak terdeteksi", "Warning")

    def check_out(self):
        self.process_frame_and_show_message("Check-Out")

    def check_in(self):
        self.process_frame_and_show_message("Check-In")

    def save_to_csv(self, name, number_id, status):
        date = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H:%M:%S")

        with open('attendance_records.csv', mode='a', newline='') as file:
            writer = csv.writer(file)

            # Check if the file is empty and write header if needed
            if file.tell() == 0:
                writer.writerow(['Name', 'ID', 'Jam', 'Tanggal', 'Status'])

            writer.writerow([name, number_id, time, date, status])

    def already_checked(self, number_id, status):
        date = datetime.now().strftime("%Y-%m-%d")

        csv_file_path = 'attendance_records.csv'

        if not os.path.exists(csv_file_path):
            return False

        with open(csv_file_path, mode='r') as file:
            reader = csv.reader(file)
            for row in reversed(list(reader)):
                if row[1] == number_id and row[3] == date:
                    return row[4] == status
        return False

    def show_unknown_message(self, icon, text, title):
        msg = QMessageBox()
        msg.setIcon(icon)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.exec_()

    def save_image(self, frame, name, id):
        # Create a folder named "face_images" if it doesn't exist
        folder_path = "face_images"
        os.makedirs(folder_path, exist_ok=True)

        # Generate a unique filename based on name, hours, and date
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{id}_{timestamp}.png"

        # Save the image in the "face_images" folder
        filepath = os.path.join(folder_path, filename)
        cv2.imwrite(filepath, frame)

        print(f"Image saved: {filename}")


if __name__ == '__main__':
    app = QApplication([])
    window = UI()
    window.show()
    app.exec_()
