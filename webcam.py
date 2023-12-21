import cv2
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
import face_recognition

from FaceRecognizer import FaceRecognizer

class CameraWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(QPixmap)

    CONFIDENCE_LEVEL = 0.6
    RECTANGLE_COLORS = {"Unknown": (0, 0, 255), "Known": (0, 255, 0)}

    def __init__(self, json_filename="model/output_encodings.json"):
        super().__init__()
        self.recognizer = FaceRecognizer(json_filename)
        self.video_capture = None
        # self.aa = camera
        self.current_frame = None  # Added attribute to store the current frame

    def set_model(self, model_filename):
        self.recognizer.load_model(model_filename)
        print(model_filename)
    def set_camera(self, camera_index):
        if self.video_capture is not None:
            self.video_capture.release()  # Release the previous camera

        self.video_capture = cv2.VideoCapture(camera_index)
        if not self.video_capture.isOpened():
            print(f"Error: Unable to open camera {camera_index}")
            self.video_capture = None  # Set to None to handle the error gracefully
            return


    def process_frame(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names, face_nameids = self.recognize_faces(face_encodings)

        return face_locations, face_names, face_nameids

    def recognize_faces(self, face_encodings):
        face_names = []
        face_nameids = []

        for face_encoding in face_encodings:
            recognition_results = self.recognizer.recognize_face(face_encoding)
            if recognition_results:
                result = recognition_results[0]
                if result['confidence'] >= self.CONFIDENCE_LEVEL:
                    face_names.append(result['name'])
                    face_nameids.append(result['numberid'])
                else:
                    face_names.append("Unknown")
                    face_nameids.append("Unknown")
            else:
                face_names.append("Unknown")
                face_nameids.append("Unknown")

        return face_names, face_nameids

    def display_results(self, frame, face_locations, face_names):
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            rectangle_color = self.RECTANGLE_COLORS.get(name, (0, 0, 255))
            text_bg_color = rectangle_color  # Set text background color based on rectangle color

            cv2.rectangle(frame, (left, top), (right, bottom), rectangle_color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), text_bg_color, cv2.FILLED)
            cv2.putText(frame, f"{name}", (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 5)

        pixmap = self.frame_to_pixmap(frame)
        self.progress.emit(pixmap)

    def frame_to_pixmap(self, frame):
        pixmap = QPixmap.fromImage(QImage(frame.data, frame.shape[1], frame.shape[0],
                                          frame.strides[0], QImage.Format_RGB888).rgbSwapped())
        return pixmap

    def run(self):
        while True:
            # print(self.video_capture)
            if self.video_capture:
                ret, frame = self.video_capture.read()
                self.current_frame = frame  # Update current_frame attribute
                if frame is not None and frame.any():
                    face_locations, face_names, nameids = self.process_frame(frame)
                    self.display_results(frame, face_locations, face_names)



# if __name__ == "__main__":
#     app = CameraWorker()
#     app.run()
