from pyspark.sql import functions as F

def limpiar(df):

    df = (
        df
        .filter(F.col("price").isNotNull())
        .filter(F.col("price") > 0)
        .filter(F.col("event_type").isNotNull())
        .dropDuplicates()
    )

    df = (
        df
        .withColumn(
            "brand",
            F.lower(F.trim(F.col("brand")))
        )
        .withColumn(
            "event_hour",
            F.hour("event_time")
        )
        .withColumn(
            "event_day",
            F.dayofweek("event_time")
        )
        .withColumn(
            "main_category",
            F.split(
                F.col("category_code"),
                "\\."
            ).getItem(0)
        )
    )

    return df