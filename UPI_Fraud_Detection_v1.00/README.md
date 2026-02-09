# UPI Fraud Detection Engine

This project is a production-style UPI fraud detection system designed to
identify suspicious and fraudulent transactions in real time.  
It uses rule-based risk scoring, explainable fraud reasons, audit logging,
and a live monitoring dashboard.

---

## 🚀 Key Features

- Real-time UPI fraud decision API (FastAPI)
- Rule-based fraud risk scoring engine
- Explainable risk factors for each decision
- RBI-style actions: ALLOW / STEP_UP_AUTH / BLOCK
- Audit logging for compliance and traceability
- Live Streamlit dashboard for monitoring transactions

---

## 🛠️ Technology Stack

- Python
- FastAPI
- Pydantic
- Streamlit
- Uvicorn

---

## 🧱 System Architecture

Client (Swagger / Dashboard)  
→ FastAPI Application  
→ Fraud Engine (Risk Scoring)  
→ Risk Reason Engine (Explainability)  
→ Decision Output  
→ Audit Logger (JSONL File)

---

## ▶️ How to Run the Project

### 1. Install dependencies
```bash
pip install -r requirements.txt
