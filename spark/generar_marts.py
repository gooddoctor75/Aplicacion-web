from spark_session import crear_spark
from limpieza import limpiar

from pyspark.sql import functions as F

spark = crear_spark()

print("Cargando CSV...")

df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv("data/raw/2019-Oct.csv")
)

print("Limpiando datos...")

df = limpiar(df)

print("Guardando dataset curado...")

df.write.mode("overwrite").parquet(
    "data/curated/ecommerce_curado.parquet"
)

print("Generando mart de categorías...")

ventas_categoria = (
    df
    .groupBy("main_category")
    .agg(
        F.count("*").alias("eventos"),
        F.sum("price").alias("ingresos")
    )
)

ventas_categoria.write.mode("overwrite").parquet(
    "data/marts/ventas_categoria.parquet"
)

print("Generando mart de marcas...")

ventas_marca = (
    df
    .filter(F.col("brand").isNotNull())
    .groupBy("brand")
    .agg(
        F.count("*").alias("eventos"),
        F.sum("price").alias("ingresos")
    )
)

ventas_marca.write.mode("overwrite").parquet(
    "data/marts/ventas_marca.parquet"
)

print("Generando funnel...")

funnel = (
    df
    .groupBy("event_type")
    .count()
)

funnel.write.mode("overwrite").parquet(
    "data/marts/funnel.parquet"
)

print("Generando actividad por hora...")

actividad_hora = (
    df
    .groupBy("event_hour")
    .count()
)

actividad_hora.write.mode("overwrite").parquet(
    "data/marts/actividad_hora.parquet"
)

print("Proceso terminado")

print("Generando heatmap hora-dia...")

heatmap = (
    df
    .groupBy("event_day", "event_hour")
    .count()
)

heatmap.write.mode("overwrite").parquet(
    "data/marts/heatmap_hora_dia.parquet"
)

print("Generando conversion por marca...")

views = (
    df
    .filter(F.col("event_type") == "view")
    .groupBy("brand")
    .count()
    .withColumnRenamed("count", "views")
)

purchases = (
    df
    .filter(F.col("event_type") == "purchase")
    .groupBy("brand")
    .count()
    .withColumnRenamed("count", "purchases")
)

conversion_marca = (
    views
    .join(purchases, "brand", "left")
    .fillna(0)
    .withColumn(
        "conversion",
        (F.col("purchases") / F.col("views")) * 100
    )
)

conversion_marca.write.mode("overwrite").parquet(
    "data/marts/conversion_marca.parquet"
)

print("Generando dataset de precios...")

precios = (
    df
    .select(
        "price",
        "main_category"
    )
)

precios.write.mode("overwrite").parquet(
    "data/marts/precios.parquet"
)