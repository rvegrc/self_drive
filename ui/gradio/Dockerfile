# app/Dockerfile

FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app

# Install the required packages
RUN pip3 install -r requirements.txt

COPY ui_gr.py .

EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"