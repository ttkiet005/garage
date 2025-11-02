# SmartGarage Server (Flask)
Server xử lý nhận dạng biển số xe từ ESP32 và giao tiếp với app Android.

## API Endpoints
- `GET /api/test` — Kiểm tra kết nối.
- `POST /api/ocr` — Gửi ảnh để nhận dạng biển số.

## Triển khai Render
1. Tạo repo GitHub, push code này lên.
2. Truy cập https://render.com → “New Web Service”.
3. Kết nối với repo → chọn branch → Build Command:  
