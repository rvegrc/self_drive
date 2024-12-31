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
ram = 20
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
    spark_submit_task = SparkSubmitOperator(
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

    

