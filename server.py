from flask import Flask, request, jsonify
import os
import cv2
import numpy as np
import easyocr
from datetime import datetime

app = Flask(__name__)

# Tạo thư mục lưu ảnh upload (nếu chưa có)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Khởi tạo EasyOCR (ngôn ngữ tiếng Anh và số)
reader = easyocr.Reader(['en'], gpu=False)

@app.route('/')
def index():
    return "✅ SmartGarage Flask Server is running!"

# ==============================
# API: Nhận ảnh từ ESP32 và xử lý OCR
# ==============================
@app.route('/api/ocr', methods=['POST'])
def ocr_plate():
    try:
        # Nhận file ảnh từ ESP32
        file = request.files.get('image')
        if not file:
            return jsonify({"status": "error", "message": "Không nhận được ảnh"}), 400

        # Lưu file
        filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Đọc ảnh
        image = cv2.imread(filepath)

        # Nhận diện biển số bằng EasyOCR
        result = reader.readtext(image)

        # Gộp các chuỗi nhận được
        text = " ".join([res[1] for res in result])

        # Trả về kết quả JSON
        return jsonify({
            "status": "success",
            "filename": filename,
            "plate_text": text
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==============================
# API: Test từ App Android
# ==============================
@app.route('/api/test', methods=['GET'])
def test_connection():
    return jsonify({"message": "SmartGarage API online!"})


# Chạy local
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
