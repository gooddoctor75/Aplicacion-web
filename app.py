import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# ──────────────────────────────────────────────
# Configuración de página
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Incidentes UAECOB Bogotá 2020",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Estilos personalizados
# ──────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        border-left: 4px solid #E63946;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 8px;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #E63946; margin: 0; }
    .metric-label { font-size: 0.85rem; color: #555; margin: 0; }
    .section-title {
        font-size: 1.1rem; font-weight: 600;
        border-bottom: 2px solid #E63946;
        padding-bottom: 6px; margin-bottom: 16px;
        color: #1a1a2e;
    }
    .insight-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 0.88rem;
        margin-top: 8px;
    }
    [data-testid="stSidebar"] { background: #1a1a2e; }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiselect label { color: #aaa !important; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Carga y limpieza de datos
# ──────────────────────────────────────────────
MESES_ES = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
    'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
    'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12,
}
MESES_NOMBRE = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
}
PALETA = px.colors.qualitative.Bold

@st.cache_data
def cargar_datos():
    df = pd.read_csv(
        'incidentes_uaecob_2020.csv',
        encoding='latin1', sep=';', low_memory=False,
    )

    # Mes numérico
    def get_mes(s):
        s = str(s).lower()
        for m, n in MESES_ES.items():
            if m in s:
                return n
        return None

    df['MES'] = df['FECHA DEL EVENTO'].apply(get_mes)
    df['MES_NOMBRE'] = df['MES'].map(MESES_NOMBRE)

    # Servicio limpio (sin número)
    df['SERVICIO_SIMPLE'] = df['SERVICIO'].str.extract(r'\d+\.\s+(.*)')

    # Tiempo de respuesta en minutos
    def parse_tiempo(s):
        try:
            parts = str(s).split(':')
            return int(parts[0]) * 60 + int(parts[1]) + int(parts[2]) / 60
        except:
            return None

    df['TIEMPO_RESP_MIN'] = df['Tiempo de Respuesta'].apply(parse_tiempo)
    # Filtrar outliers extremos (> 3 horas)
    df.loc[df['TIEMPO_RESP_MIN'] > 180, 'TIEMPO_RESP_MIN'] = None

    # Estrato numérico válido
    df['ESTRATO_NUM'] = pd.to_numeric(df['ESTRATO'], errors='coerce')

    # Causas limpias
    df['CAUSAS_LIMPIA'] = df['CAUSAS'].str.strip().str.upper()
    df.loc[~df['CAUSAS_LIMPIA'].isin(
        ['ACCIDENTAL', 'NATURAL', 'PROVOCADA', 'INDETERMINADA',
         'ORDEN', 'NO APLICA', 'CONDICIÓN HUMANA']),
        'CAUSAS_LIMPIA'] = 'OTRA'

    return df


df = cargar_datos()

# ──────────────────────────────────────────────
# Sidebar – filtros globales
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚒 Filtros")
    st.markdown("---")

    meses_disponibles = sorted([m for m in df['MES'].dropna().unique()])
    meses_sel = st.multiselect(
        "Mes",
        options=meses_disponibles,
        default=meses_disponibles,
        format_func=lambda m: MESES_NOMBRE.get(m, str(m)),
    )

    localidades = sorted(df['LOCALIDAD'].dropna().unique())
    loc_sel = st.multiselect(
        "Localidad",
        options=localidades,
        default=localidades,
    )

    estratos = ['1', '2', '3', '4', '5', '6']
    estrato_sel = st.multiselect(
        "Estrato",
        options=estratos,
        default=estratos,
    )

    st.markdown("---")
    st.markdown(
        "<small>Datos: UAECOB — Cuerpo Oficial de Bomberos de Bogotá.<br>"
        "Corte: 31 agosto 2020.</small>",
        unsafe_allow_html=True,
    )

# Aplicar filtros
mask = (
    df['MES'].isin(meses_sel) &
    df['LOCALIDAD'].isin(loc_sel) &
    df['ESTRATO'].isin(estrato_sel + ['SIN ESTRATO', 'RURAL', 'DEPARTAMENTAL'])
)
dff = df[mask].copy()

# ──────────────────────────────────────────────
# Encabezado
# ──────────────────────────────────────────────
st.markdown("# 🚒 Incidentes atendidos por UAECOB — Bogotá 2020")
st.markdown(
    "Análisis interactivo de los **{:,}** registros del Cuerpo Oficial de Bomberos "
    "de Bogotá entre enero y agosto de 2020. Usa los filtros del panel lateral para explorar.".format(len(dff))
)

# ──────────────────────────────────────────────
# Métricas KPI
# ──────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""<div class="metric-card">
        <p class="metric-value">{len(dff):,}</p>
        <p class="metric-label">Total incidentes</p>
    </div>""", unsafe_allow_html=True)
with col2:
    t_med = dff['TIEMPO_RESP_MIN'].median()
    st.markdown(f"""<div class="metric-card">
        <p class="metric-value">{t_med:.0f} min</p>
        <p class="metric-label">Tiempo de respuesta mediano</p>
    </div>""", unsafe_allow_html=True)
with col3:
    loc_top = dff['LOCALIDAD'].value_counts().idxmax() if len(dff) > 0 else "—"
    st.markdown(f"""<div class="metric-card">
        <p class="metric-value">{loc_top}</p>
        <p class="metric-label">Localidad con más incidentes</p>
    </div>""", unsafe_allow_html=True)
with col4:
    serv_top = dff['SERVICIO_SIMPLE'].value_counts().idxmax() if len(dff) > 0 else "—"
    st.markdown(f"""<div class="metric-card">
        <p class="metric-value">{serv_top.title()}</p>
        <p class="metric-label">Tipo de incidente más frecuente</p>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════
# VIZ 1: Comparación entre categorías
# Gráfico de barras horizontales — tipo de servicio
# ══════════════════════════════════════════════
st.markdown('<p class="section-title">📊 Viz 1 · Comparación: tipos de incidente atendidos</p>', unsafe_allow_html=True)

top_n = st.slider("Número de tipos a mostrar", 5, 15, 10, key="slider_v1")
conteo = (
    dff['SERVICIO_SIMPLE']
    .value_counts()
    .head(top_n)
    .reset_index()
)
conteo.columns = ['Tipo de incidente', 'Cantidad']
conteo = conteo.sort_values('Cantidad')

fig1 = px.bar(
    conteo,
    x='Cantidad',
    y='Tipo de incidente',
    orientation='h',
    color='Cantidad',
    color_continuous_scale='Reds',
    text='Cantidad',
    title=f'Top {top_n} tipos de incidente — UAECOB Bogotá 2020',
)
fig1.update_traces(textposition='outside')
fig1.update_layout(
    showlegend=False,
    coloraxis_showscale=False,
    xaxis_title='Número de incidentes',
    yaxis_title=None,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font_family='Arial',
    title_font_size=14,
    margin=dict(l=10, r=40, t=50, b=30),
    height=420,
)
fig1.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
fig1.update_yaxes(showgrid=False)

st.plotly_chart(fig1, use_container_width=True)
st.markdown("""<div class="insight-box">
💡 <b>Hallazgo:</b> La mayoría de los servicios corresponden a <b>prevenciones, activaciones y continuaciones</b>
— no a incendios reales. Los incendios propiamente dichos representan menos del 4% del total,
lo que refleja la labor preventiva y de apoyo del cuerpo de bomberos.
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════
# VIZ 2: Distribución de variable numérica
# Histograma + boxplot — tiempo de respuesta
# ══════════════════════════════════════════════
st.markdown('<p class="section-title">⏱️ Viz 2 · Distribución: tiempo de respuesta (minutos)</p>', unsafe_allow_html=True)

col_a, col_b = st.columns([3, 1])
with col_b:
    serv_options = ['Todos'] + sorted(dff['SERVICIO_SIMPLE'].dropna().unique().tolist())
    serv_fil = st.selectbox("Filtrar por tipo", serv_options, key="sel_v2")

df_t = dff.dropna(subset=['TIEMPO_RESP_MIN'])
if serv_fil != 'Todos':
    df_t = df_t[df_t['SERVICIO_SIMPLE'] == serv_fil]

with col_a:
    fig2 = go.Figure()
    fig2.add_trace(go.Histogram(
        x=df_t['TIEMPO_RESP_MIN'],
        nbinsx=40,
        marker_color='#E63946',
        opacity=0.8,
        name='Frecuencia',
    ))
    fig2.add_vline(
        x=df_t['TIEMPO_RESP_MIN'].median(),
        line_dash='dash', line_color='#1a1a2e',
        annotation_text=f"Mediana: {df_t['TIEMPO_RESP_MIN'].median():.1f} min",
        annotation_position='top right',
    )
    fig2.update_layout(
        title='Distribución del tiempo de respuesta',
        xaxis_title='Minutos desde el reporte hasta la llegada',
        yaxis_title='Número de incidentes',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=360,
        margin=dict(l=10, r=10, t=50, b=30),
        showlegend=False,
    )
    fig2.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
    fig2.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("""<div class="insight-box">
💡 <b>Hallazgo:</b> El tiempo de respuesta mediano es de <b>~9 minutos</b>, con una distribución
sesgada a la derecha — la mayoría de los incidentes se atienden en menos de 15 minutos,
pero algunos casos complejos o distantes elevan el promedio a ~11 min.
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════
# VIZ 3: Relación entre variables
# Heatmap estrato × tipo de servicio
# ══════════════════════════════════════════════
st.markdown('<p class="section-title">🔥 Viz 3 · Relación: estrato socioeconómico × tipo de incidente</p>', unsafe_allow_html=True)

top_servicios = dff['SERVICIO_SIMPLE'].value_counts().head(8).index.tolist()
df_heat = dff[
    dff['ESTRATO_NUM'].between(1, 6) &
    dff['SERVICIO_SIMPLE'].isin(top_servicios)
].copy()

pivot = (
    df_heat
    .groupby(['ESTRATO_NUM', 'SERVICIO_SIMPLE'])
    .size()
    .reset_index(name='Cantidad')
    .pivot(index='SERVICIO_SIMPLE', columns='ESTRATO_NUM', values='Cantidad')
    .fillna(0)
)
pivot.columns = [f'Estrato {int(c)}' for c in pivot.columns]

fig3 = px.imshow(
    pivot,
    color_continuous_scale='YlOrRd',
    aspect='auto',
    title='Incidentes por tipo de servicio y estrato socioeconómico',
    labels={'color': 'Incidentes', 'x': 'Estrato', 'y': 'Tipo de incidente'},
)
fig3.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    height=380,
    margin=dict(l=10, r=10, t=50, b=30),
    coloraxis_colorbar=dict(title='N.º incidentes'),
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("""<div class="insight-box">
💡 <b>Hallazgo:</b> Los estratos 2 y 3 concentran la mayor cantidad de incidentes en casi
todas las categorías — coherente con que son los estratos más poblados de Bogotá.
Los incidentes con animales y las quemas prohibidas son relativamente más frecuentes
en estratos bajos, mientras que las falsas alarmas se distribuyen de forma más uniforme.
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════
# VIZ 4: Evolución temporal
# Línea de tiempo mensual por tipo de servicio
# ══════════════════════════════════════════════
st.markdown('<p class="section-title">📅 Viz 4 · Evolución temporal: incidentes por mes</p>', unsafe_allow_html=True)

servicios_opcion = ['Todos los tipos'] + sorted(dff['SERVICIO_SIMPLE'].dropna().unique().tolist())
sel_servicio_t = st.selectbox("Ver evolución de:", servicios_opcion, key="sel_v4")

if sel_servicio_t == 'Todos los tipos':
    df_time = (
        dff.groupby(['MES', 'MES_NOMBRE'])
        .size()
        .reset_index(name='Cantidad')
        .sort_values('MES')
    )
    color_col = None
    title_t = 'Total de incidentes atendidos por mes'
else:
    df_time = (
        dff[dff['SERVICIO_SIMPLE'] == sel_servicio_t]
        .groupby(['MES', 'MES_NOMBRE'])
        .size()
        .reset_index(name='Cantidad')
        .sort_values('MES')
    )
    color_col = None
    title_t = f'Incidentes de tipo "{sel_servicio_t}" por mes'

fig4 = go.Figure()
fig4.add_trace(go.Scatter(
    x=df_time['MES_NOMBRE'],
    y=df_time['Cantidad'],
    mode='lines+markers+text',
    line=dict(color='#E63946', width=3),
    marker=dict(size=9, color='#1a1a2e'),
    text=df_time['Cantidad'],
    textposition='top center',
    name='Incidentes',
))
# Banda cuarentena
fig4.add_vrect(
    x0='Marzo', x1='Abril',
    fillcolor='#457b9d', opacity=0.1,
    annotation_text='Inicio cuarentena COVID-19',
    annotation_position='top left',
    annotation_font_size=11,
)
fig4.update_layout(
    title=title_t,
    xaxis_title='Mes',
    yaxis_title='Número de incidentes',
    plot_bgcolor='white',
    paper_bgcolor='white',
    height=380,
    margin=dict(l=10, r=10, t=50, b=30),
    showlegend=False,
    hovermode='x',
)
fig4.update_xaxes(showgrid=False)
fig4.update_yaxes(showgrid=True, gridcolor='#f0f0f0')

st.plotly_chart(fig4, use_container_width=True)

st.markdown("""<div class="insight-box">
💡 <b>Hallazgo:</b> Se observa una <b>reducción notable en marzo y abril</b>, coincidiendo con el
inicio de la cuarentena obligatoria por COVID-19. Algunos tipos de incidentes como incendios
y quemas prohibidas muestran patrones estacionales propios del verano bogotano (enero–febrero).
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════
# VIZ 5: Composición / proporciones
# Treemap: localidad + tipo de servicio
# ══════════════════════════════════════════════
st.markdown('<p class="section-title">🗺️ Viz 5 · Composición: distribución geográfica por localidad y tipo</p>', unsafe_allow_html=True)

col_c, col_d = st.columns([1, 3])
with col_c:
    top_loc = st.slider("Top localidades", 5, 20, 10, key="slider_v5")
    mostrar_por = st.radio("Desglose por", ['Tipo de incidente', 'Causa', 'Estrato'], key="radio_v5")

top_localidades = dff['LOCALIDAD'].value_counts().head(top_loc).index.tolist()
df_tree = dff[dff['LOCALIDAD'].isin(top_localidades)].copy()

if mostrar_por == 'Tipo de incidente':
    path_col = 'SERVICIO_SIMPLE'
elif mostrar_por == 'Causa':
    path_col = 'CAUSAS_LIMPIA'
else:
    df_tree['ESTRATO_LABEL'] = 'Estrato ' + df_tree['ESTRATO'].astype(str)
    path_col = 'ESTRATO_LABEL'

df_tree_grouped = (
    df_tree
    .groupby(['LOCALIDAD', path_col])
    .size()
    .reset_index(name='Cantidad')
)

with col_d:
    fig5 = px.treemap(
        df_tree_grouped,
        path=['LOCALIDAD', path_col],
        values='Cantidad',
        color='Cantidad',
        color_continuous_scale='Reds',
        title=f'Composición de incidentes — top {top_loc} localidades',
    )
    fig5.update_layout(
        paper_bgcolor='white',
        height=480,
        margin=dict(l=0, r=0, t=50, b=10),
    )
    fig5.update_traces(
        textinfo='label+value',
        hovertemplate='<b>%{label}</b><br>Incidentes: %{value}<extra></extra>',
    )
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("""<div class="insight-box">
💡 <b>Hallazgo:</b> <b>Suba y Kennedy</b> juntas concentran casi el 20% de todos los incidentes
registrados. El tipo de incidente dominante varía por localidad: en zonas con más industria
(Fontibón, Puente Aranda) hay mayor proporción de MATPEL (materiales peligrosos),
mientras que en localidades periféricas predominan quemas prohibidas e incidentes con animales.
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ──────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#999; font-size:0.8rem; padding: 20px 0 10px;">
    Fuente: Datos Abiertos Bogotá · UAECOB (Cuerpo Oficial de Bomberos) · Corte 31 agosto 2020<br>
    Herramientas y Visualización de Datos — Fundación Universitaria Los Libertadores
</div>
""", unsafe_allow_html=True)
