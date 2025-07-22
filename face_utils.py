import face_recognition
import mediapipe as mp
import cv2
import numpy as np

mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.7)

def detect_faces_mediapipe(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_detection.process(rgb)
    boxes = []
    if results.detections:
        h, w, _ = frame.shape
        for detection in results.detections:
            box = detection.location_data.relative_bounding_box
            x1 = int(box.xmin * w)
            y1 = int(box.ymin * h)
            x2 = x1 + int(box.width * w)
            y2 = y1 + int(box.height * h)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            boxes.append((x1, y1, x2, y2))
    return boxes

def encode_face(frame, box):
    x1, y1, x2, y2 = box
    face_img = frame[y1:y2, x1:x2]
    rgb_face = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb_face)
    if encodings:
        return encodings[0]
    return None

def encode_face_pil(img_np):
    encodings = face_recognition.face_encodings(img_np)
    if encodings:
        return encodings[0]
    return None

def recognize_face(face_encoding, known_students, tolerance=0.5):
    filtered_students = [s for s in known_students if 'encoding' in s]
    encodings = [s['encoding'] for s in filtered_students]
    if not encodings:
        return None, None
    matches = face_recognition.compare_faces(encodings, face_encoding, tolerance)
    if True in matches:
        idx = matches.index(True)
        return filtered_students[idx]['id'], filtered_students[idx]['name']
    return None, None