import face_recognition
import numpy as np
import cv2

known_encodings = []
known_ids = []

def load_known_faces_from_sheet(emp_rows):
    global known_encodings, known_ids
    known_encodings = []
    known_ids = []

    for row in emp_rows:
        emp_id = row.get("Employee ID")
        img_url = row.get("Employee Picture")

        if not img_url:
            continue

        import requests
        r = requests.get(img_url, timeout=10)
        image_np = np.asarray(bytearray(r.content), dtype=np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        encs = face_recognition.face_encodings(image)
        if len(encs) == 1:
            known_encodings.append(encs[0])
            known_ids.append(emp_id)
