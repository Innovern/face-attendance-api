from flask import Flask, request, jsonify
import requests, os, json
from utils.face_utils import load_known_faces, recognize_face
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Load employee faces
load_known_faces()

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

@app.route("/recognize", methods=["POST"])
def recognize():
    data = request.json
    image_url = data.get("image_url")
    sn = data.get("sn")

    if not image_url:
        return jsonify({"error": "Image URL missing"}), 400

    img_path = f"{TEMP_DIR}/{sn}.jpg"

    r = requests.get(image_url)
    with open(img_path, "wb") as f:
        f.write(r.content)

    emp_id, result = recognize_face(img_path)
    write_temp_upload(image_url, result, emp_id)

    return jsonify({
        "sn": sn,
        "result": result,
        "employee_id": emp_id
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
