import os
from datetime import datetime

import cv2
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QMessageBox, QComboBox, QListView
from PyQt5.QtCore import Qt, QThread, QStringListModel

from trainData import FaceEncodingScanner
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

        self.train_worker = FaceEncodingScanner()
        self.train_thread = QThread()
        self.setup_train_thread()

        self.button_check_in = self.findChild(QPushButton, 'buttonCheckIn')
        self.button_check_in.clicked.connect(self.check_in)

        self.button_check_out = self.findChild(QPushButton, 'buttonCheckOut')
        self.button_check_out.clicked.connect(self.check_out)

        self.combo_box_camera = self.findChild(QComboBox, 'comboBoxCamera')
        self.combo_box_model = self.findChild(QComboBox, 'comboBoxModel')

        self.list_cameras()
        self.list_model()

        self.combo_box_camera.currentIndexChanged.connect(self.update_camera)

        self.combo_box_model.currentIndexChanged.connect(self.update_model)


        self.button_train_data = self.findChild(QPushButton, 'buttonTrainNewData')
        self.button_train_data.clicked.connect(self.train_data)

        # self.listview_log = QListView(self)
        self.model = QStringListModel()

        self.listview_log = self.findChild(QListView, 'listViewLog')
        self.listview_log.setModel(self.model)
        # self.add_item("item1")

    def list_model(self):
        self.combo_box_model.clear()
        for filename in os.listdir("model"):
            if filename.endswith(".json"):
                print(filename)
                self.combo_box_model.addItem(filename)

    def add_item(self, item):
        # Get the current string list
        string_list = self.model.stringList()

        # Add the new item to the list
        string_list.append(item)

        # Update the model with the modified list
        self.model.setStringList(string_list)

    def train_data(self):
        json_filename = "model/output_encodings"

        self.train_worker.run(json_filename)
        self.list_model()
        print("Processing started")

    def list_cameras(self):
        for i in range(10):  # Assume up to 10 cameras, adjust as needed
            cap = cv2.VideoCapture(i)
            if not cap.isOpened():
                break
            print(f"Camera {i}")
            self.combo_box_camera.addItem(f"Camera {i}")

            cap.release()

    def update_model(self):
        selected_model_index = self.combo_box_model.currentText()
        self.camera_worker.set_model(selected_model_index)

    def update_camera(self):
        selected_camera_index = self.combo_box_camera.currentIndex()
        self.camera_worker.set_camera(selected_camera_index)

    def setup_camera_thread(self):
        self.label_camera = self.findChild(QLabel, 'labelCamera')
        setup_thread(self.camera_worker,
                     self.camera_thread,
                     self.camera_worker.run,
                     self.camera_thread.quit,
                     self.camera_worker.deleteLater,
                     self.set_label_camera)

    def setup_train_thread(self):
        setup_thread(self.train_worker,
                     self.train_thread,
                     self.train_worker.run,
                     self.train_thread.quit,
                     self.train_worker.deleteLater,
                     self.train_data)

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
                    self.add_item(message)
                    # self.listview_log.
                else:
                    message = f"Anda sudah {check_type} hari ini"
                    success_message = QMessageBox.Warning
                    self.add_item(message)
                self.show_unknown_message(success_message, message,
                                          "Warning" if success_message == QMessageBox.Warning else "Success")
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
