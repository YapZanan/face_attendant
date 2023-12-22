from datetime import datetime

from PyQt5.QtCore import QObject, pyqtSignal, QThread
import os
import json
import face_recognition
import numpy as np


def extract_name_and_numberid(filename):
    # Assuming the filename format is "name_numberid.jpg"
    name, rest = filename.split('_', 1)
    numberid, _ = rest.split('.', 1)
    return name, numberid


def get_face_encodings(image_path):
    try:
        print("ab")
        print(image_path)
        image = face_recognition.load_image_file(image_path)
        print("cd")
        face_encodings = face_recognition.face_encodings(image)
        print("ef")
        return face_encodings
    except Exception as e:
        print(f"Exception in get_face_encodings: {e}")
        return []


class FaceEncodingScanner(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, folder_path="images"):
        super().__init__()
        self.folder_path = folder_path
        self.face_encodings_data = []

    def process_images(self):
        total_files = len([filename for filename in os.listdir(self.folder_path) if filename.endswith(".jpg")])
        print(total_files)
        # Iterate over each file in the folder
        try:
            print("benar")
            for idx, filename in enumerate(os.listdir(self.folder_path)):
                print("ya")
                if filename.endswith(".jpg"):
                    print("aaaabbb")
                    file_path = os.path.join(self.folder_path, filename)
                    # Extract name and numberid from the filename
                    print("c")
                    name, numberid = extract_name_and_numberid(filename)
                    print("d")
                    # Process the image and get face encodings

                    encodings = get_face_encodings(file_path)
                    print("e")

                    # Convert the list of face encodings to a NumPy array
                    print("f")
                    encodings_array = np.array(encodings)

                    # Save data to the list
                    print("g")
                    self.face_encodings_data.append(
                        {'name': name, 'numberid': numberid, 'encodings': encodings_array.tolist()})
                    print("h")
                    # Emit progress signal
                    self.progress.emit(int((idx + 1) / total_files * 100))
                    print(int((idx + 1) / total_files * 100))
            date = datetime.now().strftime("%Y%m%d")
            time = datetime.now().strftime("%H%M%S")
            # Emit finished signal when processing is complete
            self.save_to_json(f"model/output_encodings_{date}_{time}.json")
            self.finished.emit()
            print("finished")
        except Exception as e:
            print(f"Exception: {e}")

    def save_to_json(self, json_filename="aa.json"):
        with open(json_filename, 'w') as jsonfile:
            json.dump(self.face_encodings_data, jsonfile, default=lambda x: x.tolist())
            print("done")