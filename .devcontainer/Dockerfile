FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-ben tesseract-ocr-eng ffmpeg \
    fonts-dejavu-core libglib2.0-0 libgl1 \
    && rm -rf /var/lib/apt/lists/*
