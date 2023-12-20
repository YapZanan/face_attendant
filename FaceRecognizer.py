import json
import face_recognition

from trainData import get_face_encodings


class FaceRecognizer:
    def __init__(self, json_filename):
        self.json_filename = json_filename
        self.face_encodings_data = self.load_json_data()

    def load_json_data(self):
        with open(self.json_filename, 'r') as jsonfile:
            face_encodings_data = json.load(jsonfile)
        return face_encodings_data

    def recognize_face(self, trained_encodings, tolerance=0.6):
        results = []

        for data in self.face_encodings_data:
            # Use face_recognition.face_distance to get the face distance
            face_distances = face_recognition.face_distance(data['encodings'], trained_encodings)
            matches = list(face_distances <= tolerance)

            # If any match is found, add the result and break the loop
            if any(matches):
                index = matches.index(True)
                confidence = 1 - face_distances[index]  # Convert face distance to confidence level
                results.append({
                    'name': data['name'],
                    'numberid': data['numberid'],
                    'match_index': index,
                    'confidence': confidence
                })

        return results


# Example usage
if __name__ == "__main__":
    json_filename = "output_encodings.json"
    test_image_path = "images/jokowi_14.jpg"

    recognizer = FaceRecognizer(json_filename)
    recognition_results = recognizer.recognize_face(test_image_path)

    if recognition_results:
        for result in recognition_results:
            if result['confidence'] >= 0.8:  # Set your desired confidence threshold
                print("Face recognized! Details:")
                print(f"Name: {result['name']}, NumberID: {result['numberid']}, Confidence: {result['confidence']:.2%}")
            else:
                print("No match found. Confidence below 80%.")
    else:
        print("No match found.")

