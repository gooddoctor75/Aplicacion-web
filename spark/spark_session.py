from pyspark.sql import SparkSession

def crear_spark():

    spark = (
        SparkSession.builder
        .appName("EcommerceAnalytics")
        .config("spark.driver.memory", "8g")
        .config("spark.executor.memory", "8g")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    return spark