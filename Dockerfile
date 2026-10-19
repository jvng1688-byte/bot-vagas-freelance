FROM python:3.11-slim

# Instala dependências do sistema para Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Instala Playwright e browsers
RUN pip install playwright==1.46.0
RUN playwright install chromium
RUN playwright install-deps chromium

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]