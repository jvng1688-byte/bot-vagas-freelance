FROM python:3.11-slim

# Instala dependências do sistema para Playwright (Chromium)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    libglib2.0-0 \
    libgobject-2.0-0 \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libgio-2.0-0 \
    libdrm2 \
    libexpat1 \
    libxcb1 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    fonts-liberation2 \
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

# Instala Playwright e browsers
RUN pip install playwright==1.46.0
RUN playwright install chromium

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]