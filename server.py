from flask import Flask, request, jsonify, send_from_directory
import cv2
import pytesseract
import os
import re
from datetime import datetime

app = Flask(__name__)

# Thư mục lưu ảnh
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return "✅ SmartGarage OCR Server running!"


# ============================================
# ✅ API: Upload ảnh & Nhận diện biển số
# ============================================
@app.route("/recognize", methods=["POST"])
def recognize_plate():
    file = request.files.get("image")
    if not file:
        return jsonify({"status": "error", "message": "Không nhận được file ảnh"}), 400

    # Tạo tên ảnh
    filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # Lưu ảnh
    file.save(filepath)

    # Đọc ảnh bằng OpenCV
    img = cv2.imread(filepath)

    # =======================
    # ✅ Tiền xử lý ảnh
    # =======================
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    gray = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    # =======================
    # ✅ OCR nhận diện biển số
    # =======================
    config = r'-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 --psm 7'
    text = pytesseract.image_to_string(gray, config=config)

    # Chỉ lấy ký tự hợp lệ A–Z, 0–9
    plate = re.sub(r'[^A-Z0-9]', '', text).strip()

    return jsonify({
        "status": "success",
        "filename": filename,
        "plate_text": plate
    })


# ============================================
# ✅ API: Xem Gallery (danh sách ảnh đã upload)
# ============================================
@app.route("/gallery", methods=["GET"])
def gallery():
    files = os.listdir(UPLOAD_FOLDER)
    files.sort(reverse=True)

    file_urls = [
        {
            "file": filename,
            "url": f"/uploads/{filename}"
        }
        for filename in files
    ]

    return jsonify({
        "status": "success",
        "images": file_urls
    })


# ============================================
# ✅ API: Xem từng ảnh trong thư mục uploads
# ============================================
@app.route("/uploads/<filename>")
def get_uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ============================================
# ✅ Chạy local
# ============================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
