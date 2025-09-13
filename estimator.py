import cv2
import mediapipe as mp
import numpy as np

class HeadPoseEstimator:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.blink_threshold = 0.25

    def euclidean_distance(self, p1, p2):
        return np.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

    def compute_ear(self, eye):
        v1 = self.euclidean_distance(eye[1], eye[5])
        v2 = self.euclidean_distance(eye[2], eye[4])
        h = self.euclidean_distance(eye[0], eye[3])
        return (v1 + v2) / (2.0 * h)

    def get_direction(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if results.multi_face_landmarks:
            face = results.multi_face_landmarks[0]
            nose = face.landmark[1]

            left_eye = [face.landmark[i] for i in [362, 385, 387, 263, 373, 380]]
            right_eye = [face.landmark[i] for i in [33, 160, 158, 133, 153, 144]]
            left_ear = self.compute_ear(left_eye)
            right_ear = self.compute_ear(right_eye)
            ear = (left_ear + right_ear) / 2.0

            blink = 1 if ear < self.blink_threshold else 0

            return f"{nose.x:.2f},{nose.y:.2f},{blink}"

        return "0.5,0.5,0"