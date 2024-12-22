FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

# 
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 
COPY api.py .

# COPY ../.env .

# EXPOSE 8000

# app is fastapi instance api is the file name
