FROM python:3.12-bullseye

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system & build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    build-essential \
    pkg-config \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libavfilter-dev \
    libswscale-dev \
    libswresample-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install dependencies first for better caching
COPY requirements.txt .

RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

# Create a non-root user before assigning ownership
RUN useradd -m -d /home/appuser -s /bin/bash appuser

# Create app directories and set permissions
RUN mkdir -p /app/logs /app/data /app/temp /home/appuser/.cache && \
    chown -R appuser:appuser /app /home/appuser && \
    chmod -R 755 /app/logs /app/data /app/temp

# Copy source code after dependencies
COPY . .

# Switch to non-root user
USER appuser

EXPOSE 5000

# Healthcheck for container monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "app_streaming.py"]
