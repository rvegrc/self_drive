from fastapi import FastAPI
import os
import joblib
import pandas as pd

root_path = "."
CH_IP = os.getenv('CH_IP')
CH_USER = os.getenv('CH_USER')
CH_PASS = os.getenv('CH_PASS')

import mlflow
# client = mlflow.MlflowClient(tracking_uri='http://127.0.0.1:8888') # for saving mlruns in local webserver
# mlflow.set_tracking_uri='http://127.0.0.1:8888'
your_mlflow_tracking_uri = f'{root_path}/mlruns' 
mlflow.set_tracking_uri(your_mlflow_tracking_uri)

app = FastAPI() # name of the FastAPI instance

# load model from mlflow


import joblib
import clickhouse_connect

client = clickhouse_connect.get_client(host=CH_IP, port=8123, username=CH_USER, password=CH_PASS)

app = FastAPI() # name of the FastAPI instance

# load list of model from clickhouse
# models = client.query_df('select * from transerv_dev.measure_service_values_flag') # create db for system files

# load model from mlflow



@app.get("/")
def read_root():

    return {"Hello": "World"}


@app.get("/dataset")
def read_dataset(dataset_id: str):
    # model_loaded = joblib.load('./best_model.pkl')   
    return {"origin": dataset_id, "new": dataset_id + '11111'}

@app.get("/test")
def read_test():
    return {"Hello": "Test"}