from fastapi import FastAPI
import os
import joblib
import pandas as pd

import mlflow
# client = mlflow.MlflowClient(tracking_uri='http://127.0.0.1:8888') # for saving mlruns in local webserver
# mlflow.set_tracking_uri='http://127.0.0.1:8888'

app = FastAPI() # name of the FastAPI instance

# load model from mlflow


import joblib
import clickhouse_connect

client = clickhouse_connect.get_client(host=CH_IP, port=8123, username=CH_USER, password=CH_PASS)

app = FastAPI() # name of the FastAPI instance

# load file from clickhouse
measure_service_values_flag = client.query_df('select * from transerv_dev.measure_service_values_flag') # create db for system files

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