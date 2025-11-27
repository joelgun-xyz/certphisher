# Certphisher - Dockerfile
# Multi-stage build for optimized image size

FROM python:3.11-slim as base

# Install system dependencies including Chrome for Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome/Chromium environment variables
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p /app/app/uploads \
    && mkdir -p /data/mongodb \
    && chmod -R 755 /app

# Expose ports
# 5000 for Flask frontend
EXPOSE 5000

# Default command (can be overridden in docker-compose)
CMD ["python3", "main.py"]
