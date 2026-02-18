# ─── Segmentation Model (PyTorch / MONAI batch pipeline) ─────────────────────
FROM python:3.11-slim

WORKDIR /app

# System dependencies for PyTorch, nibabel, trimesh, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full segmentation model directory
COPY . .

# Default: run the full inference pipeline
# Override CMD or use docker run args to run individual scripts
CMD ["python", "Inference_Pipeline/run_pipeline.py"]
