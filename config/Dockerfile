FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for pygame, opencv, etc.
RUN apt-get update && apt-get install -y \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libsmpeg-dev \
    libportmidi-dev \
    libavformat-dev \
    libswscale-dev \
    libfreetype6-dev \
    libx11-dev \
    xvfb \
    x11-utils \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# We don't need to copy all files since we'll mount them as volumes
# COPY . .

# Set display environment variable
ENV DISPLAY=:1

# Use a simple bash script as the command
CMD ["bash", "-c", "echo 'Starting snake game...'; if ! timeout 2 xdpyinfo >/dev/null 2>&1; then echo 'Using virtual framebuffer'; Xvfb :1 -screen 0 1280x720x24 -ac & sleep 1; fi; python src/main_web.py --mode=human"] 