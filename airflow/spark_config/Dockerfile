# FROM bitnami/spark:latest
# FROM apache/spark:3.5.4-scala2.12-java17-python3-ubuntu
FROM bitnami/spark:3.5.4-debian-12-r0
# USER root


RUN pip install --upgrade pip
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
