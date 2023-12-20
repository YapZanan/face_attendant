import cv2
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
import face_recognition

from FaceRecognizer import FaceRecognizer


class CameraWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(QPixmap)

    def __init__(self, json_filename="output_encodings.json", ConfidenceLevel=0.6):
        super().__init__()
        self.ConfidenceLevel = ConfidenceLevel
        self.recognizer = FaceRecognizer(json_filename)
        self.video_capture = cv2.VideoCapture(0)

    def process_frame(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            name = self.recognize_face(face_encoding)
            face_names.append(name)

        return face_locations, face_names

    def recognize_face(self, face_encoding):
        recognition_results = self.recognizer.recognize_face(face_encoding)
        if recognition_results:
            result = recognition_results[0]
            if result['confidence'] >= self.ConfidenceLevel:
                return result['name']
        return "Unknown"

    def display_results(self, frame, face_locations, face_names):
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            if name == "Unknown":
                # Draw a red rectangle for unknown faces
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                text_bg_color = (0, 0, 255)  # Red background for unknown faces
            else:
                # Draw a green rectangle for known faces
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                text_bg_color = (0, 255, 0)  # Green background for known faces

            label = f"{name}"
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), text_bg_color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, label, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 5)

        pixmap = self.frame_to_pixmap(frame)
        self.progress.emit(pixmap)

    def frame_to_pixmap(self, frame):
        pixmap = QPixmap.fromImage(QImage(frame.data, frame.shape[1], frame.shape[0],
                                          frame.strides[0], QImage.Format_RGB888).rgbSwapped())
        return pixmap

    def run(self):
        while True:
            ret, frame = self.video_capture.read()

            face_locations, face_names = self.process_frame(frame)
            self.display_results(frame, face_locations, face_names)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.video_capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    app = CameraWorker()
    app.run()
