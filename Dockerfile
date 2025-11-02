FROM python:3.10-slim

WORKDIR /app

# Install dependencies for OpenCV
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python3", "main.py"]
