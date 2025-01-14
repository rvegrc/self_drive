from pendulum import datetime, duration
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from lib.clickhouse_operator_extended import ClickHouseOperatorExtended
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from pyspark.sql import SparkSession
from pyspark import SparkContext
import pandas as pd

CLICKHOUSE_CONN_ID = 'clickhouse'
SPARK_CONN_ID = 'spark'





default_args={
    "owner": "rvegrc",
    "depends_on_past": False,
    "retries": 0
}
ram = 5
cpu = 30*3
@dag(
    tags=["test", "stocks"],
    render_template_as_native_obj=True,
    max_active_runs=1,
    #schedule='50 2 * * *',
    schedule=None,
    default_args=default_args,
    start_date=datetime(2023, 12, 1),
    template_searchpath='dags/include', 
    catchup=False,
    description='testing connection',
    doc_md=__doc__
)
def spark_clickhouse_test():
    # packages = [
    # "com.clickhouse.spark:clickhouse-spark-runtime-3.5_2.12:0.8.0"
    # ,"com.clickhouse:clickhouse-jdbc:0.7.1-patch1"
    # ,"com.clickhouse:clickhouse-http-client:0.7.1-patch1"
    # ,"org.apache.httpcomponents.client5:httpclient5:5.3.1"
    # # ,"ai.catboost:catboost-spark_3.5_2.12:1.2.7"
    # # ,"com.microsoft.azure:synapseml_2.12:1.0.8" 
    # ]
    packages = ["com.clickhouse.spark:clickhouse-spark-runtime-3.5_2.12:0.8.0",
    "com.clickhouse:clickhouse-jdbc:0.7.0",
    "com.clickhouse:clickhouse-client:0.7.0",
    "com.clickhouse:clickhouse-http-client:0.7.0",
    "org.apache.httpcomponents.client5:httpclient5:5.2.1",
    'org.apache.sedona:sedona-spark-3.5_2.12:1.7.0',
    'org.datasyslab:geotools-wrapper:1.7.0-28.5',
    'uk.co.gresearch.spark:spark-extension_2.12:2.11.0-3.4'
    ]



    spark_submit_task = SparkSubmitOperator(
        packages= ','.join(packages),
        task_id='spark_submit_task',
        application='dags/spark_app/spark_1.py',
        #conn_id='spark_master',
        conn_id=SPARK_CONN_ID,        
        total_executor_cores='1',
        executor_cores='1',
        executor_memory=f'{ram}g',
        num_executors='1',
        driver_memory=f'{ram}g',
        verbose=True
    )
    
    clickhouse_test_conn = ClickHouseOperatorExtended(
        task_id='clickhouse_test_conn',
        clickhouse_conn_id=CLICKHOUSE_CONN_ID,
        sql='test.sql'
    )

    @task.pyspark(conn_id=SPARK_CONN_ID)
    def run(spark: SparkSession, sc: SparkContext) -> pd.DataFrame:
        # spark = SparkSession.builder.appName("ExampleJob111").getOrCreate()
        root = "/opt/airflow"
        data = [("Alice", 1), ("Bob", 2), ("Charlie", 3)]
        df = spark.createDataFrame(data, ["Name", "Value"])
        df.write.parquet(f"{root}/test/test", mode="overwrite")
        df = spark.read.parquet(f"{root}/test/test")
        df.show()
        #show all folders in the current directory
            
        df.toPandas().to_csv(f"{root}/test/df_test1.csv", index=False)
        spark.stop()
        return pd.read_csv(f"{root}/test/df_test1.csv")


    [spark_submit_task, clickhouse_test_conn] >> run()

spark_clickhouse_test()

    

