FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY UPI_Fraud_Detection_v1.0/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY UPI_Fraud_Detection_v1.0/app ./app
COPY UPI_Fraud_Detection_v1.0/init_db.py .
COPY UPI_Fraud_Detection_v1.0/dashboard.py .

EXPOSE 10000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]

