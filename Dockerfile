FROM python:3.11-slim

# --------------------------------------------------
# Working directory
# --------------------------------------------------
WORKDIR /app

# --------------------------------------------------
# System dependencies
# --------------------------------------------------
RUN apt-get update && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------
# Python dependencies
# --------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --------------------------------------------------
# Copy application code
# --------------------------------------------------
COPY app ./app
COPY init_db.py .

# --------------------------------------------------
# Expose port (Render)
# --------------------------------------------------
EXPOSE 10000

# --------------------------------------------------
# Init DB ONCE, then start FastAPI
# --------------------------------------------------
CMD python init_db.py && \
    uvicorn app.main:app --host 0.0.0.0 --port 10000
