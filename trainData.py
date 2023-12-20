import os
import json
import face_recognition
import numpy as np

3
def extract_name_and_numberid(filename):
    # Assuming the filename format is "name_numberid.jpg"
    name, rest = filename.split('_', 1)
    numberid, _ = rest.split('.', 1)
    return name, numberid


def get_face_encodings(image_path):
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)
    return face_encodings


class FaceEncodingScanner:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.face_encodings_data = []

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

    def save_to_json(self, json_filename):
        with open(json_filename, 'w') as jsonfile:
            json.dump(self.face_encodings_data, jsonfile, default=lambda x: x.tolist())


# Example usage
if __name__ == "__main__":
    folder_path = "images"
    json_filename = "output_encodings.json"

    scanner = FaceEncodingScanner(folder_path)
    scanner.process_images()
    scanner.save_to_json(json_filename)
