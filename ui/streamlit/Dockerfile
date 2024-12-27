# app/Dockerfile

FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install the required packages
RUN pip install -r requirements.txt

COPY ui_st.py .

EXPOSE 8501

# Add a health check (ensure your app responds to this endpoint)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# # Run the streamlit app for name of file use only '_' not '-'
# ENTRYPOINT ["streamlit", "run", "ui_st.py", "--server.port=8501", "--server.address=0.0.0.0", "--browser.gatherUsageStats", "false"]