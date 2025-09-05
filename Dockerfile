FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# Install system dependencies (FFmpeg required for Whisper/audio-extract)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Upgrade pip and install dependencies
# Pre-install torch from official wheels to avoid building from source
# Install NumPy 1.x first to ensure compatibility
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir "numpy<2.0.0" \
    && pip install --no-cache-dir torch==2.2.0+cpu torchvision==0.17.0+cpu \
       -f https://download.pytorch.org/whl/cpu/torch_stable.html \
    && pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

EXPOSE 8000

CMD ["python", "run.py"]
