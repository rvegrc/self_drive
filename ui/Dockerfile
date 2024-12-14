# app/Dockerfile

FROM python:3.10-slim

WORKDIR /app

COPY . /app/

RUN pip3 install -r requirements.txt

EXPOSE 45000

HEALTHCHECK CMD curl --fail http://localhost:45000/_stcore/health

ENTRYPOINT ["streamlit", "run", "ui.py", "--server.port=45000", "--server.address=0.0.0.0"]