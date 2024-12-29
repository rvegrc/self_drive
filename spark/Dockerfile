# FROM apache/spark:3.4.2-scala2.12-java11-python3-ubuntu 
FROM apache/spark:3.5.4-scala2.12-java17-python3-ubuntu
# FROM bitnami/spark:3.5.4-debian-12-r0



WORKDIR /app

USER root
# FROM apache/sedona:latest
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# COPY .env .
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=19888", "--no-browser", "--allow-root", "--NotebookApp.token='1234'", "--NotebookApp.password='1234'"]