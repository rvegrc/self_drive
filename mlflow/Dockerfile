FROM python:3.10-slim
WORKDIR /app

USER root

COPY requirements.txt .

# RUN apt-get -y update
# RUN apt-get -y install git

RUN pip install --no-cache-dir -r requirements.txt 