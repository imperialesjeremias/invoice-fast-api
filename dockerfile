FROM python:3.9

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    unzip \
    yasm \
    pkg-config \
    libswscale-dev \
    libtbb-dev \
    libjpeg-dev \ 
    libpng-dev \
    libtiff-dev \
    libavformat-dev \
    libpq-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poppler, Python3, pip y dependencias necesarias
RUN apt-get update && \
    apt-get install -y poppler-utils tesseract-ocr python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

RUN pip install numpy opencv-python

WORKDIR /app/
COPY ./requirements.txt /app/requirements.txt
COPY ./ /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache

