# app/Dockerfile

FROM python:3.11-slim

WORKDIR /app

COPY . /app/

# COPY ../ds_salary/data/job_title.csv /app/

# COPY ../ds_salary/data/country_name.csv /app/

RUN pip3 install -r requirements.txt

EXPOSE 45000

HEALTHCHECK CMD curl --fail http://localhost:45000/_stcore/health

ENTRYPOINT ["streamlit", "run", "ui.py", "--server.port=45000", "--server.address=0.0.0.0"]