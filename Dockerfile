FROM python:3.10-slim

# Cài Tesseract OCR và các thư viện cần thiết
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục ứng dụng
WORKDIR /app

# Copy file yêu cầu
COPY requirements.txt .

# Cài Python libs
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ server vào container
COPY . .

# Expose port
EXPOSE 5000

# Lệnh chạy (Gunicorn cho production)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app"]
