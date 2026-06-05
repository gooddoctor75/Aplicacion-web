import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# =====================================================
# CONFIGURACIÓN STREAMLIT
# =====================================================

st.set_page_config(
    page_title="Ecommerce Clickstream Analytics",
    layout="wide"
)

st.title("🛒 Ecommerce Clickstream Analytics")
st.markdown("Análisis de comportamiento de usuarios usando PySpark")

# =====================================================
# SPARK
# =====================================================

@st.cache_resource
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


spark = crear_spark()

# =====================================================
# CARGA DATOS
# =====================================================

@st.cache_resource
def cargar_datos():

    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv("data/2019-Oct.csv")
    )

    return df


# =====================================================
# LIMPIEZA
# =====================================================

@st.cache_resource
def limpiar_datos(df):

    df_limpio = (
        df
        .filter(F.col("price").isNotNull())
        .filter(F.col("price") > 0)
        .filter(F.col("event_type").isNotNull())
        .dropDuplicates()
        .withColumn(
            "event_hour",
            F.hour("event_time")
        )
        .withColumn(
            "brand",
            F.lower(F.trim(F.col("brand")))
        )
        .withColumn(
            "main_category",
            F.split(
                F.col("category_code"),
                "\\."
            ).getItem(0)
        )
    )

    df_limpio.cache()
    df_limpio.count()

    return df_limpio


with st.spinner("Cargando dataset..."):

    df = cargar_datos()
    df_limpio = limpiar_datos(df)

# =====================================================
# MÉTRICAS
# =====================================================

@st.cache_data
def obtener_metricas():

    total_registros = df_limpio.count()

    total_usuarios = (
        df_limpio
        .select("user_id")
        .distinct()
        .count()
    )

    total_categorias = (
        df_limpio
        .select("main_category")
        .distinct()
        .count()
    )

    return (
        total_registros,
        total_usuarios,
        total_categorias
    )


registros, usuarios, categorias = obtener_metricas()

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("Opciones")

muestra = st.sidebar.slider(
    "Filas a visualizar",
    5,
    100,
    20
)

# =====================================================
# MÉTRICAS VISUALES
# =====================================================

c1, c2, c3 = st.columns(3)

c1.metric(
    "Registros",
    f"{registros:,}"
)

c2.metric(
    "Usuarios",
    f"{usuarios:,}"
)

c3.metric(
    "Categorías",
    f"{categorias:,}"
)

# =====================================================
# TABS
# =====================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "Dataset",
        "Eventos",
        "Horas",
        "Marcas",
        "Categorías",
        "Heatmap"
    ]
)

# =====================================================
# TAB DATASET
# =====================================================

with tab1:

    st.subheader("Vista previa")

    muestra_df = (
        df_limpio
        .limit(muestra)
        .toPandas()
    )

    st.dataframe(
        muestra_df,
        use_container_width=True
    )

# =====================================================
# GRÁFICO 1
# EVENTOS
# =====================================================

@st.cache_data
def datos_eventos():

    return (
        df_limpio
        .groupBy("event_type")
        .count()
        .orderBy(F.desc("count"))
        .toPandas()
    )


with tab2:

    eventos = datos_eventos()

    fig, ax = plt.subplots(
        figsize=(10, 5)
    )

    sns.barplot(
        data=eventos,
        x="event_type",
        y="count",
        ax=ax
    )

    ax.set_title(
        "Distribución de Eventos"
    )

    st.pyplot(fig)

# =====================================================
# GRÁFICO 2
# HORAS
# =====================================================

@st.cache_data
def datos_horas():

    return (
        df_limpio
        .groupBy("event_hour")
        .count()
        .orderBy("event_hour")
        .toPandas()
    )


with tab3:

    horas = datos_horas()

    fig, ax = plt.subplots(
        figsize=(12, 5)
    )

    sns.lineplot(
        data=horas,
        x="event_hour",
        y="count",
        marker="o",
        ax=ax
    )

    ax.set_title(
        "Actividad por Hora"
    )

    st.pyplot(fig)

# =====================================================
# GRÁFICO 3
# MARCAS
# =====================================================

@st.cache_data
def top_marcas():

    return (
        df_limpio
        .filter(
            F.col("brand").isNotNull()
        )
        .groupBy("brand")
        .count()
        .orderBy(
            F.desc("count")
        )
        .limit(10)
        .toPandas()
    )


with tab4:

    marcas = top_marcas()

    fig, ax = plt.subplots(
        figsize=(12, 5)
    )

    sns.barplot(
        data=marcas,
        x="brand",
        y="count",
        ax=ax
    )

    plt.xticks(rotation=45)

    ax.set_title(
        "Top 10 Marcas"
    )

    st.pyplot(fig)

# =====================================================
# GRÁFICO 4
# CATEGORÍAS
# =====================================================

@st.cache_data
def top_categorias():

    return (
        df_limpio
        .groupBy("main_category")
        .count()
        .orderBy(
            F.desc("count")
        )
        .limit(10)
        .toPandas()
    )


with tab5:

    categorias_df = top_categorias()

    fig, ax = plt.subplots(
        figsize=(12, 5)
    )

    sns.barplot(
        data=categorias_df,
        x="main_category",
        y="count",
        ax=ax
    )

    plt.xticks(rotation=45)

    ax.set_title(
        "Top Categorías"
    )

    st.pyplot(fig)

# =====================================================
# GRÁFICO 5
# HEATMAP
# =====================================================

@st.cache_data
def datos_heatmap():

    datos = (
        df_limpio
        .groupBy(
            "main_category",
            "event_type"
        )
        .agg(
            F.avg("price")
            .alias("avg_price")
        )
        .toPandas()
    )

    return datos


with tab6:

    heat = datos_heatmap()

    pivot = heat.pivot(
        index="main_category",
        columns="event_type",
        values="avg_price"
    )

    fig, ax = plt.subplots(
        figsize=(12, 7)
    )

    sns.heatmap(
        pivot,
        annot=True,
        cmap="Blues",
        ax=ax
    )

    ax.set_title(
        "Precio Promedio por Categoría y Evento"
    )

    st.pyplot(fig)
