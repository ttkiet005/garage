from flask import Flask, request, jsonify, send_from_directory
import os
import cv2
import numpy as np
from datetime import datetime
from ultralytics import YOLO
from paddleocr import PaddleOCR

app = Flask(__name__)

# Thư mục lưu ảnh upload
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load model YOLO nhận diện biển số
plate_detector = YOLO("yolov8n.pt")   # Hoặc model đã train riêng nếu có

# OCR
ocr = PaddleOCR(lang="en")  # biển số VN = chữ + số, en là phù hợp nhất

@app.route("/")
def home():
    return "✅ SmartGarage AI Plate Recognition Server Running!"

# ============================
# API: Upload & Recognize Plate
# ============================
@app.route("/recognize", methods=["POST"])
def recognize_plate():
    file = request.files.get("image")

    if not file:
        return jsonify({"error": "No image received"}), 400

    filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Load ảnh
    img = cv2.imread(filepath)

    # ---------- Detect Plate with YOLO --------------
    results = plate_detector.predict(img, conf=0.5)

    plates = []
    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        plates.append((x1, y1, x2, y2))

    if not plates:
        return jsonify({"status": "failed", "message": "No plate detected"}), 200

    # Cắt vùng biển số (lấy cái lớn nhất)
    x1, y1, x2, y2 = plates[0]
    plate_crop = img[y1:y2, x1:x2]

    # ---------- OCR bằng PaddleOCR --------------
    ocr_result = ocr.ocr(plate_crop)

    text = ""
    if ocr_result:
        for line in ocr_result:
            for word in line:
                text += word[1][0] + " "

    text = text.strip()

    return jsonify({
        "status": "success",
        "filename": filename,
        "plate_text": text,
        "box": [x1, y1, x2, y2]
    })

# ============================
# Gallery xem ảnh đã upload
# ============================
@app.route("/gallery")
def gallery():
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify({"images": files})

@app.route("/uploads/<path:filename>")
def get_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
