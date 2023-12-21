import os
import json
from datetime import datetime

import face_recognition
import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QPixmap


def extract_name_and_numberid(filename):
    # Assuming the filename format is "name_numberid.jpg"
    name, rest = filename.split('_', 1)
    numberid, _ = rest.split('.', 1)
    return name, numberid


def get_face_encodings(image_path):
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)
    return face_encodings


class FaceEncodingScanner(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(QPixmap)

    def __init__(self):
        super().__init__()
        self.folder_path = "images"
        self.face_encodings_data = []
        # self.json_filename =   # Make json_filename an instance variable

    def process_images(self):
        # Iterate over each file in the folder
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".jpg"):
                file_path = os.path.join(self.folder_path, filename)
                # Extract name and numberid from the filename
                name, numberid = extract_name_and_numberid(filename)
                # Process the image and get face encodings
                encodings = get_face_encodings(file_path)

                # Convert the list of face encodings to a NumPy array
                encodings_array = np.array(encodings)

                # Save data to the list
                self.face_encodings_data.append(
                    {'name': name, 'numberid': numberid, 'encodings': encodings_array.tolist()})

    def save_to_json(self, json_name):
        date = datetime.now().strftime("%Y%m%d")
        time = datetime.now().strftime("%H%M%S")
        json_filename_with_timestamp = f"{json_name}_{date}_{time}.json"

        with open(json_filename_with_timestamp, 'w') as jsonfile:
            json.dump(self.face_encodings_data, jsonfile, default=lambda x: x.tolist())

    def run(self, json_name):
        self.process_images()
        self.save_to_json(json_name)
        self.finished.emit()
