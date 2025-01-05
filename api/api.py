from fastapi import FastAPI, HTTPException

from pydantic import BaseModel
from typing import List, Dict


import os
import joblib
import pandas as pd




root_path = "."
preprocessor_path = 'preprocessor'

CH_IP = os.getenv('CH_IP')
CH_USER = os.getenv('CH_USER')
CH_PASS = os.getenv('CH_PASS')


from union_dfs import union_dfs
from df_preprocess import df_preprocess


# # Spark initialize
# import findspark
# findspark.init()

# from pyspark.sql import SparkSession

# from pyspark.sql import functions as F
# from pyspark.sql import DataFrame as SparkDataFrame
# import os

# # ml
# from pyspark.ml import Pipeline as spk_pipeline
# from pyspark.ml.feature import VectorAssembler as spk_VectorAssembler


# packages = [
#     "com.clickhouse.spark:clickhouse-spark-runtime-3.5_2.12:0.8.0"
#     ,"com.clickhouse:clickhouse-jdbc:0.7.1-patch1"
#     ,"com.clickhouse:clickhouse-http-client:0.7.1-patch1"
#     ,"org.apache.httpcomponents.client5:httpclient5:5.3.1"
#     # ,"ai.catboost:catboost-spark_3.5_2.12:1.2.7"
#     # ,"com.microsoft.azure:synapseml_2.12:1.0.8"

# ]

# ram = 5
# # cpu = 22*3
# # Define the application name and setup session
# appName = "Connect To ClickHouse via PySpark"
# spark = (SparkSession.builder
#         .appName(appName)
#         .config("spark.jars.packages", ",".join(packages))
#         .config("spark.sql.catalog.clickhouse", "com.clickhouse.spark.ClickHouseCatalog")
#         .config("spark.sql.catalog.clickhouse.host", CH_IP)
#         .config("spark.sql.catalog.clickhouse.protocol", "http")
#         .config("spark.sql.catalog.clickhouse.http_port", "8123")
#         .config("spark.sql.catalog.clickhouse.user", CH_USER)
#         .config("spark.sql.catalog.clickhouse.password", CH_PASS)
#         .config("spark.sql.catalog.clickhouse.database", "default")
#         .config("spark.executor.memory", f"{ram}g")
#         .config("spark.driver.maxResultSize", f"{ram}g")
#         .config("spark.driver.memory", f"{ram}g")
#         .config("spark.executor.memoryOverhead", f"{ram}g")
#         .getOrCreate()
# )

# spark.sql("use clickhouse")

# from synapse.ml.lightgbm import LightGBMRegressor as LightGBMRegressor_spark


import joblib
import clickhouse_connect


import mlflow
# client = mlflow.MlflowClient(tracking_uri='http://127.0.0.1:8888') # for saving mlruns in local webserver
# mlflow.set_tracking_uri='http://127.0.0.1:8888'
your_mlflow_tracking_uri = f'{root_path}/mlruns' 
mlflow.set_tracking_uri(your_mlflow_tracking_uri)

client = clickhouse_connect.get_client(host=CH_IP, port=8123, username=CH_USER, password=CH_PASS)


app = FastAPI() # name of the FastAPI instance

# load list of model from clickhouse
# models = client.query_df('select * from transerv_dev.measure_service_values_flag') # create db for system files


class DataFrameInput(BaseModel):
    data: List[Dict]  # Expecting a list of dictionaries as input


@app.post("/get_df")
async def get_df(ids: List[int], targets: List[str]):
    try:
        df_list = []
        for id in ids:
            control = client.query_df(f'''
                select * 
                from ycup.control yc
                where yc.id = {id}
                limit 10'''
            )

            localizations = client.query_df(f'''
                select * 
                from ycup.localization yl
                where yl.id = {id}
                limit 10'''
            )

            metadata = client.query_df(f'''
                select * 
                from ycup.metadata ym
                where ym.id = {id}
                limit 10'''
            )
            # add df by id to list
            df_list.append(union_dfs(control, localizations, metadata)) 

        df = pd.concat(df_list, ignore_index=True)    
                            
        df_prepr = {}
        for target in targets:
            df_prepr[target] = df_preprocess(df, target, id, preprocessor_path)

                    
        # test return for one target
        return df_prepr[target].to_json(orient='records')   
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
