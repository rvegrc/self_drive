from pyspark.sql import SparkSession
import os
def run():
    spark = SparkSession.builder.appName("ExampleJob111").getOrCreate()
    root = "/opt/airflow"
    data = [("Alice", 1), ("Bob", 2), ("Charlie", 3)]
    df = spark.createDataFrame(data, ["Name", "Value"])
    df.write.parquet(f"{root}/test/test", mode="overwrite")
    df = spark.read.parquet(f"{root}/test/test")
    df.show()


    #show all folders in the current directory
    

    
    df.toPandas().to_csv(f"{root}/test/df_test1.csv", index=False)
    spark.stop()
    return


# start only if you run the file, if the file would be instead imported the run command will be ignored 
if __name__ == "__main__":
    run()