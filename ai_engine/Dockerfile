# ─── AI Engine (Flask) ────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# System dependencies required by PyTorch / spaCy / faiss
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (including the scispaCy model URL)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

EXPOSE 5000

ENV FLASK_ENV=production

CMD ["python", "app.py"]
