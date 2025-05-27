FROM python:3.9-slim

WORKDIR /app

RUN apt update && apt install -y \
    python3-dev \
    build-essential \
    scons \
    libjpeg-dev \
    libopenjp2-7 \
    libtiff5 \
    libatlas-base-dev \
    libffi-dev \
    libfreetype6-dev \
    libportaudio2 \
    libturbojpeg \
    && apt clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "led_ui.py", "--server.enableCORS=false"]
