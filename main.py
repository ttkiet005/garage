from flask import Flask, request, jsonify, send_from_directory
import os
import cv2
from datetime import datetime
from ultralytics import YOLO
from paddleocr import PaddleOCR

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load YOLO (dùng YOLOv8n để nhẹ)
plate_detector = YOLO("yolov8n.pt")

# OCR Lite (không dùng paddlepaddle nên rất nhẹ)
ocr = PaddleOCR(use_angle_cls=True, lang='en', rec_model_dir=None, det_model_dir=None)

@app.route("/")
def home():
    return "✅ SmartGarage AI Plate Recognition Server Running (PaddleOCR Lite)"

@app.route("/recognize", methods=["POST"])
def recognize():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No file received"}), 400

    filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    img = cv2.imread(filepath)

    # Detect plate using YOLO
    results = plate_detector.predict(img, conf=0.4)
    boxes = results[0].boxes

    if len(boxes) == 0:
        return jsonify({"status": "failed", "plate_text": "No plate detected"})

    # Crop biggest detection
    box = boxes[0].xyxy[0].tolist()
    x1, y1, x2, y2 = map(int, box)
    crop = img[y1:y2, x1:x2]

    # OCR
    result = ocr.ocr(crop, cls=True)
    text = ""
    if result:
        for line in result:
            for word in line:
                text += word[1][0] + " "

    return jsonify({
        "status": "success",
        "filename": filename,
        "plate_text": text.strip(),
        "box": [x1, y1, x2, y2]
    })

@app.route("/gallery")
def gallery():
    return jsonify({"images": os.listdir(UPLOAD_FOLDER)})

@app.route("/uploads/<path:filename>")
def get_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
