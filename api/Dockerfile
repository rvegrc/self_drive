# FROM python:3.10-slim
FROM bitnami/spark:3.5.4-debian-12-r0

USER root

# Set working directory
WORKDIR /app


COPY requirements.txt .

# 
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 
COPY api.py .
COPY get_df_from_db.py .
COPY df_preprocess.py .

# COPY ../.env .

# EXPOSE 8000

# app is fastapi instance api is the file name
