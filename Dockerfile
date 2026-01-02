# ---------- Base image ----------
FROM python:3.10-slim

# ---------- System dependencies ----------
# libgomp1 is REQUIRED for LightGBM
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgomp1 \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# ---------- Environment ----------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---------- Working directory ----------
WORKDIR /app

# ---------- Install Python dependencies ----------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Copy project ----------
COPY . .

# ---------- Expose port ----------
EXPOSE 8000

# ---------- Start server ----------
#CMD ["sh", "-c", "uvicorn cpm_predictor.backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
CMD ["uvicorn", "cpm_predictor.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]


