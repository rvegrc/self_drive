# app/Dockerfile

FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app

# Install the required packages
RUN pip3 install -r requirements.txt

COPY ui-gr.py .

# EXPOSE 8501