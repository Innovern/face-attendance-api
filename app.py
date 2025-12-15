from flask import Flask, request, jsonify
import requests, os, json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from utils.face_utils import load_known_faces_from_sheet
import face_recognition
import numpy as np
import cv2

app = Flask(__name__)
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

def get_emp_data():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = json.loads(os.environ["GOOGLE_CREDS_JSON"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    sheet = client.open("YOUR_SHEET_NAME").worksheet("Emp")
    return sheet.get_all_records()

def write_temp_upload(image_url, result, emp_id):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = json.loads(os.environ["GOOGLE_CREDS_JSON"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    sheet = client.open("IE-Projects V-2.0").worksheet("TempUploads")
    sheet.append_row([image_url, True, result, emp_id or ""])

# Load faces at startup
emp_rows = get_emp_data()
load_known_faces_from_sheet(emp_rows)

@app.route("/recognize", methods=["POST"])
def recognize():
    data = request.json
    image_url = data.get("image_url")
    sn = data.get("sn")

    if not image_url:
        return jsonify({"error": "Image URL missing"}), 400

    r = requests.get(image_url, timeout=10)
    img_np = np.asarray(bytearray(r.content), dtype=np.uint8)
    img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

    encs = face_recognition.face_encodings(img)
    if len(encs) == 0:
        result, emp_id = "NO_FACE", None
    elif len(encs) > 1:
        result, emp_id = "MULTIPLE_FACE", None
    else:
        matches = face_recognition.compare_faces(
            face_recognition.face_encodings(img),
            encs[0],
            tolerance=0.5
        )
        if True in matches:
            emp_id = emp_rows[matches.index(True)]["Employee ID"]
            result = "SUCCESS"
        else:
            emp_id = None
            result = "FAIL"

    write_temp_upload(image_url, result, emp_id)

    return jsonify({
        "result": result,
        "employee_id": emp_id
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
