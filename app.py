from flask import Flask, request, jsonify
import face_recognition, numpy as np, requests, io
from PIL import Image

app = Flask(__name__)

known_encodings = []
known_ids = []

@app.route("/recognize", methods=["POST"])
def recognize():
    data = request.json
    image_url = data["image_url"]

    img_data = requests.get(image_url).content
    img = np.array(Image.open(io.BytesIO(img_data)))

    encodings = face_recognition.face_encodings(img)

    if not encodings:
        return jsonify({"result": "No Face"})

    face = encodings[0]
    matches = face_recognition.compare_faces(
        known_encodings, face, tolerance=0.45
    )

    if True in matches:
        idx = matches.index(True)
        return jsonify({
            "result": "Matched",
            "student_id": known_ids[idx]
        })

    return jsonify({"result": "Unknown"})

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    image_url = data["image_url"]
    student_id = data["student_id"]

    img_data = requests.get(image_url).content
    img = np.array(Image.open(io.BytesIO(img_data)))

    encodings = face_recognition.face_encodings(img)

    if len(encodings) != 1:
        return {"error": "Exactly one face required"}

    encoding_str = ",".join(map(str, encodings[0]))

    # Will save to Google Sheet later
    print("Registered:", student_id)

    return {"status": "Registered"}

app.run()
