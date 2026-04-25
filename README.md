# Incidentes UAECOB Bogotá 2020 — Streamlit App

## Descripción

Aplicación web interactiva desarrollada con **Streamlit** y **Plotly** que visualiza los incidentes atendidos por la Unidad Administrativa Especial Cuerpo Oficial de Bomberos de Bogotá (UAECOB) entre enero y agosto de 2020.

Proyecto desarrollado para el curso **Herramientas y Visualización de Datos** — Fundación Universitaria Los Libertadores.

## Dataset

- **Fuente**: Datos Abiertos del Gobierno Colombiano
- **URL**: https://www.datos.gov.co/
- **Nombre**: Incidentes atendidos por UAECOB — Corte 31 agosto 2020
- **Descripción**: 20.228 registros de incidentes atendidos por el Cuerpo de Bomberos de Bogotá, con variables de fecha, localidad, estrato, tipo de servicio, causa, tiempo de respuesta y víctimas.
- **Variables**: 42 columnas — fechas, localización geográfica (barrio, UPZ, localidad, estrato), tipo de servicio, causa del incidente, y conteos de personas expuestas/afectadas/rescatadas/heridas.

## Hallazgos Principales

1. **Prevenciones y activaciones dominan**: Más del 30% de los servicios son prevenciones o activaciones de alarmas — los incendios reales representan menos del 4% del total, reflejando la labor preventiva del cuerpo de bomberos.
2. **Tiempo de respuesta mediano: 9 minutos**: La distribución está sesgada a la derecha; la mayoría de incidentes se atienden en menos de 15 minutos, pero casos complejos elevan el promedio a ~11 min.
3. **Estratos 2 y 3 concentran la mayoría de incidentes**: Coherente con su mayor población en Bogotá. Los incidentes con animales y quemas prohibidas son relativamente más frecuentes en estratos bajos.
4. **Caída de incidentes en marzo–abril por COVID-19**: La cuarentena obligatoria redujo significativamente la actividad registrada, especialmente en tipos relacionados con tráfico y espacios públicos.
5. **Suba y Kennedy lideran geográficamente**: Estas dos localidades concentran ~20% de todos los incidentes. El perfil de riesgo varía por zona: más MATPEL en zonas industriales, más quemas y animales en la periferia.

## Visualizaciones Implementadas

1. **Gráfico de barras horizontales** — Comparación de tipos de incidente (Viz 1): muestra las categorías de servicio ordenadas por frecuencia, con selector interactivo de cuántos tipos mostrar.
2. **Histograma con línea de mediana** — Distribución del tiempo de respuesta (Viz 2): permite filtrar por tipo de incidente para comparar la distribución según la complejidad del servicio.
3. **Mapa de calor (heatmap)** — Relación estrato × tipo de incidente (Viz 3): matriz de color que revela qué tipos de incidente son más frecuentes en cada estrato socioeconómico.
4. **Línea de tiempo** — Evolución mensual de incidentes (Viz 4): muestra el efecto de la cuarentena COVID-19 en la cantidad de servicios atendidos mes a mes.
5. **Treemap** — Composición geográfica por localidad (Viz 5): desglose jerárquico de incidentes por localidad y tipo/causa/estrato, con controles interactivos.

## Tecnologías Utilizadas

- **Framework**: Streamlit 1.32+
- **Lenguaje**: Python 3.10+
- **Bibliotecas principales**:
  - `plotly` — visualizaciones interactivas
  - `pandas` — manipulación y análisis de datos

## Instalación y Ejecución Local

### Requisitos Previos

- Python 3.10 o superior
- pip

### Instrucciones

```bash
# Clonar repositorio
git clone https://github.com/TU_USUARIO/uaecob-streamlit.git
cd uaecob-streamlit

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`

## Despliegue

URL en producción: *(agregar después del deploy en Streamlit Community Cloud)*

### Cómo desplegar en Streamlit Cloud

1. Subir este repositorio a GitHub (asegurarse de incluir el CSV)
2. Ir a https://share.streamlit.io
3. Conectar la cuenta de GitHub
4. Seleccionar el repositorio y el archivo `app.py` como punto de entrada
5. Hacer clic en "Deploy"

## Estructura del Repositorio

```
uaecob-streamlit/
├── app.py                                          # Aplicación principal
├── requirements.txt                                # Dependencias Python
├── incidentes_uaecob_2020.csv                      # Dataset
└── README.md                                       # Este archivo
```

## Autores

- Nombre Apellido 1
- Nombre Apellido 2

*Fundación Universitaria Los Libertadores — Herramientas y Visualización de Datos*
