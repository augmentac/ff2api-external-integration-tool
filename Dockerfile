FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for zero-cost anti-scraping
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    wget \
    gnupg \
    unzip \
    xvfb \
    tor \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libnss3-dev \
    libgconf-2-4 \
    libxss1 \
    libxtst6 \
    libxrandr2 \
    libasound2-dev \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome for JavaScript rendering
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
COPY requirements_zero_cost.txt .

# Install core dependencies first
RUN pip install --no-cache-dir -r requirements.txt

# Install zero-cost dependencies (with error handling for optional packages)
RUN pip install --no-cache-dir -r requirements_zero_cost.txt || \
    echo "Some zero-cost dependencies failed to install - continuing with core functionality"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/uploads data/mappings data/logs config

# Create TOR configuration
RUN mkdir -p /etc/tor && \
    echo "ControlPort 9051" > /etc/tor/torrc && \
    echo "CookieAuthentication 1" >> /etc/tor/torrc

# Set environment variables for zero-cost system
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/google-chrome-stable
ENV CHROMIUM_BIN=/usr/bin/google-chrome-stable
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8501

# Create startup script
RUN echo '#!/bin/bash\n\
# Start TOR in background\n\
tor --RunAsDaemon 1 --DataDirectory /tmp/tor_data --ControlPort 9051 --CookieAuthentication 1 &\n\
\n\
# Start Xvfb for headless browser support\n\
Xvfb :99 -screen 0 1024x768x24 &\n\
\n\
# Wait for services to start\n\
sleep 5\n\
\n\
# Run the application\n\
streamlit run src/frontend/app.py --server.port=8501 --server.address=0.0.0.0' > /app/start_zero_cost.sh

RUN chmod +x /app/start_zero_cost.sh

# Run the zero-cost startup script
CMD ["/app/start_zero_cost.sh"] 