"""
UAECOB Bogotá D.C. — Dashboard de Incidentes 2020
Autores: Juan Carlos Rojas Lizarazo · Brayan Andres Sierra Zambrano
Fuente: Unidad Administrativa Especial Cuerpo Oficial de Bomberos Bogotá
Dataset: https://datosabiertos.bogota.gov.co/dataset/incidente-atendido-por-bomberos
Periodo: Enero – Agosto 2020
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import unicodedata
import matplotlib.colors as mcolors

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="UAECOB · Dashboard 2020",
    page_icon="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Escudo_de_Bogot%C3%A1.svg/200px-Escudo_de_Bogot%C3%A1.svg.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paleta institucional ─────────────────────────────────────────────────────
C = {
    "azul":    "#3266ad",
    "morado":  "#7c5cbf",
    "verde":   "#1D9E75",
    "ambar":   "#BA7517",
    "rojo":    "#E24B4A",
    "teal":    "#2AB5A0",
    "naranja": "#EF9F27",
    "gris":    "#888780",
    "navy":    "#0d2b5e",
}

MESES_ES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
}
NOMBRE_MES = {1:"Ene", 2:"Feb", 3:"Mar", 4:"Abr", 5:"May", 6:"Jun", 7:"Jul", 8:"Ago"}

# ── CSS Global ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d2b5e 0%, #1a4080 60%, #1e4d96 100%);
    border-right: 1px solid #ffffff14;
  }
  [data-testid="stSidebar"] * { color: #dce8f5 !important; }
  [data-testid="stSidebar"] hr { border-color: #ffffff20; }

  /* Radio buttons del sidebar */
  [data-testid="stSidebar"] .stRadio > label { display: none; }
  [data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    font-size: 0.78rem !important;
    color: #b0c8e8 !important;
    font-weight: 400 !important;
  }
  [data-testid="stSidebar"] .stRadio label {
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 6px 10px !important;
    border-radius: 7px !important;
    transition: background 0.15s !important;
  }
  [data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.08) !important;
  }

  /* ── KPI cards ── */
  .kpi-card {
    background: #ffffff;
    border-left: 4px solid #3266ad;
    border-radius: 10px;
    padding: 18px 22px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    margin-bottom: 10px;
    transition: box-shadow .2s;
  }
  .kpi-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.12); }
  .kpi-num   { font-size: 2.1rem; font-weight: 700; line-height: 1.1; }
  .kpi-label { font-size: 0.74rem; color: #6b7280; margin-top: 4px; letter-spacing: .3px; }

  /* ── Pill title ── */
  .chart-pill {
    display: inline-block;
    background: #3266ad;
    color: #fff !important;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 3px 12px;
    border-radius: 20px;
    margin-bottom: 6px;
  }
  .chart-title {
    font-size: 1.22rem;
    font-weight: 700;
    color: #0d2b5e;
    margin: 0 0 4px;
  }
  .chart-subtitle {
    font-size: 0.80rem;
    color: #6b7280;
    margin-bottom: 18px;
  }

  /* ── Analysis cards ── */
  .analysis-card {
    border-radius: 10px;
    padding: 15px;
    border-top: 3px solid;
    height: 100%;
  }
  .card-contexto       { background:#dbeafe; border-color:#3b82f6; }
  .card-analisis       { background:#fef3c7; border-color:#f59e0b; }
  .card-interpretacion { background:#dcfce7; border-color:#22c55e; }
  .card-conclusion     { background:#ede9fe; border-color:#8b5cf6; }
  .card-label {
    font-size: 0.64rem; font-weight: 700; letter-spacing: .8px;
    text-transform: uppercase; margin-bottom: 6px;
  }
  .card-text { font-size: 0.76rem; line-height: 1.58; color: #1e293b; }

  /* ── Source footer ── */
  .source-bar {
    font-size: 0.68rem;
    color: #9ca3af;
    border-top: 1px solid #e5e7eb;
    padding-top: 8px;
    margin-top: 4px;
  }

  /* ── Page header ── */
  .page-header {
    background: linear-gradient(135deg, #0d2b5e 0%, #1a5ea8 100%);
    border-radius: 12px;
    padding: 22px 32px;
    margin-bottom: 22px;
    color: white;
  }
  .header-title { font-size: 1.5rem; font-weight: 700; color: #fff; margin: 0; }
  .header-sub   { font-size: 0.80rem; color: #aec6e8; margin-top: 4px; }

  /* ── Sidebar brand block ── */
  .sb-brand {
    padding: 4px 0 12px 0;
    border-bottom: 1px solid rgba(255,255,255,0.12);
    margin-bottom: 16px;
  }
  .sb-title {
    font-size: 1.05rem; font-weight: 700; color: #fff !important;
    letter-spacing: .5px; margin: 0;
  }
  .sb-sub {
    font-size: 0.70rem; color: #8badd4 !important; margin-top: 2px;
  }
  .sb-section {
    font-size: 0.60rem; font-weight: 700; letter-spacing: 1.4px;
    text-transform: uppercase; color: #6a90b8 !important;
    margin: 18px 0 8px; padding-left: 2px;
  }
  .sb-footer {
    font-size: 0.68rem; color: #6a90b8 !important;
    border-top: 1px solid rgba(255,255,255,0.10);
    padding-top: 12px; margin-top: 8px; line-height: 1.6;
  }

  /* ── Divider ── */
  .section-sep {
    height: 2px;
    background: linear-gradient(90deg,#3266ad,transparent);
    border: none;
    margin: 24px 0 18px;
  }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DATOS
# ══════════════════════════════════════════════════════════════════════════════
def parse_fecha(s: str):
    try:
        partes = str(s).strip().split(" de ")
        dia  = int(partes[0].split()[-1])
        mes  = MESES_ES[partes[1].lower()]
        anio = int(partes[2])
        return pd.Timestamp(year=anio, month=mes, day=dia)
    except Exception:
        return pd.NaT

def unificar_localidad(nombre):
    if pd.isna(nombre): return nombre
    partes = str(nombre).strip().split(" ", 1)
    if partes[0].isdigit() and len(partes) > 1:
        return partes[1].strip()
    return nombre.strip()

@st.cache_data(show_spinner="Cargando datos del dataset UAECOB...")
def cargar_datos() -> pd.DataFrame:
    df = pd.read_csv(
        "incidentes-atendidos-por-uaecob-corte-31-agosto-2020.csv",
        encoding="latin1", sep=";", low_memory=False,
    )
    df["FECHA"]       = df["FECHA DEL EVENTO"].apply(parse_fecha)
    df["MES"]         = df["FECHA"].dt.month
    df["HORA"]        = pd.to_datetime(df["Hora reporte"], format="%H:%M:%S", errors="coerce").dt.hour
    df["LOCALIDAD_L"] = df["LOCALIDAD"].apply(unificar_localidad)
    df["ESTRATO_NUM"] = pd.to_numeric(df["ESTRATO"], errors="coerce")
    df["TR_min"]      = (pd.to_timedelta(df["Tiempo de Respuesta"].str.strip(), errors="coerce")
                         .dt.total_seconds() / 60)
    df["TR_limpio"]   = df["TR_min"].where(df["TR_min"] <= 120)
    cols_her = ["HOMBRES HERIDOS","MUJERES HERIDAS","MENORES NIÑAS HERIDAS","MENORES NIÑOS HERIDOS"]
    cols_res = ["HOMBRES RESCATADOS","MUJERES RESCATADAS","MENORES NIÑAS RESCATADAS","MENORES NIÑOS RESCATADOS"]
    for c in cols_her + cols_res:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df["TOTAL_HERIDOS"]    = df[cols_her].sum(axis=1)
    df["TOTAL_RESCATADOS"] = df[cols_res].sum(axis=1)
    return df

df = cargar_datos()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — Profesional, sin emojis en opciones, sin filtros globales
# ══════════════════════════════════════════════════════════════════════════════
GRAFICAS = {
    "Grafica 1  ·  Incidentes por mes":          "g1",
    "Grafica 2  ·  Distribucion horaria":        "g3",
    "Grafica 3  ·  Tiempo de respuesta":         "g5",
    "Grafica 4  ·  Tipo de servicio":            "g6",
    "Grafica 5  ·  Mapa de calor por localidad": "g10",
}

with st.sidebar:
    # Escudo — usando st.markdown con img tag evita el "0" de st.image
    st.markdown(
        '<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/'
        'Escudo_de_Bogot%C3%A1.svg/200px-Escudo_de_Bogot%C3%A1.svg.png" '
        'width="52" style="display:block;margin-bottom:10px">',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sb-brand">'
        '<div class="sb-title">UAECOB · Bogotá D.C.</div>'
        '<div class="sb-sub">Dashboard de Incidentes &nbsp;·&nbsp; Ene–Ago 2020</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sb-section">Visualizaciones</div>', unsafe_allow_html=True)

    grafica_sel_label = st.radio(
        "Seleccionar grafica",
        options=list(GRAFICAS.keys()),
        label_visibility="collapsed",
    )
    grafica_sel = GRAFICAS[grafica_sel_label]

    st.markdown(
        '<div class="sb-footer">'
        'Fuente: Datos Abiertos Bogotá<br>'
        'UAECOB · Corte 31 agosto 2020<br><br>'
        'Autores:<br>'
        'J.C. Rojas Lizarazo<br>'
        'B.A. Sierra Zambrano<br>'
        'Fund. Univ. Los Libertadores · 2026'
        '</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# ENCABEZADO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="page-header">
  <div class="header-title">Dashboard de Incidentes · UAECOB Bogotá D.C.</div>
  <div class="header-sub">
    Unidad Administrativa Especial Cuerpo Oficial de Bomberos &nbsp;·&nbsp;
    Periodo: Enero – Agosto 2020 &nbsp;·&nbsp;
    <a href="https://datosabiertos.bogota.gov.co/dataset/incidente-atendido-por-bomberos"
       style="color:#7ec8e3">Datos Abiertos Bogotá</a>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs globales (dataset completo, sin filtros) ────────────────────────────
total      = len(df)
heridos    = int(df["TOTAL_HERIDOS"].sum())
rescatados = int(df["TOTAL_RESCATADOS"].sum())
tr_med     = df["TR_limpio"].median()
tr_str     = f"{tr_med:.1f} min" if pd.notna(tr_med) else "N/D"

k1, k2, k3, k4 = st.columns(4)
for col, num, label, color in [
    (k1, f"{total:,}",      "Total de incidentes",         C["azul"]),
    (k2, f"{heridos:,}",    "Personas heridas",            C["rojo"]),
    (k3, f"{rescatados:,}", "Personas rescatadas",         C["verde"]),
    (k4, tr_str,            "Tiempo de respuesta mediano", C["ambar"]),
]:
    with col:
        st.markdown(
            f'<div class="kpi-card" style="border-color:{color}">'
            f'<div class="kpi-num" style="color:{color}">{num}</div>'
            f'<div class="kpi-label">{label}</div></div>',
            unsafe_allow_html=True,
        )

st.markdown('<hr class="section-sep">', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def render_analisis(contexto, analisis, interpretacion, conclusion):
    cards = [
        ("Contexto",       contexto,       "card-contexto",       "#1e40af"),
        ("Analisis",       analisis,       "card-analisis",       "#92400e"),
        ("Interpretacion", interpretacion, "card-interpretacion", "#166534"),
        ("Conclusion",     conclusion,     "card-conclusion",     "#5b21b6"),
    ]
    cols = st.columns(4)
    for col, (label, text, css_class, color) in zip(cols, cards):
        with col:
            st.markdown(
                f'<div class="analysis-card {css_class}">'
                f'<div class="card-label" style="color:{color}">{label}</div>'
                f'<div class="card-text">{text}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

def chart_header(pill_text, title, subtitle):
    st.markdown(f'<span class="chart-pill">{pill_text}</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-subtitle">{subtitle}</div>', unsafe_allow_html=True)

LAYOUT_BASE = dict(
    plot_bgcolor="white", paper_bgcolor="white",
    font_family="Inter", font_size=12,
    margin=dict(t=20, b=40, l=20, r=20),
    hoverlabel=dict(bgcolor="white", font_size=12),
)

SOURCE = (
    '<div class="source-bar">'
    'Fuente: UAECOB · Datos Abiertos Bogotá · Periodo: Enero–Agosto 2020'
    '</div>'
)


# ══════════════════════════════════════════════════════════════════════════════
# GRAFICA 1 — Incidentes por mes
# ══════════════════════════════════════════════════════════════════════════════
if grafica_sel == "g1":
    chart_header(
        "Grafica 1 · Evolucion temporal",
        "Incidentes por mes — UAECOB Bogotá 2020",
        "Volumen mensual de incidentes atendidos entre enero y agosto de 2020."
    )

    por_mes = df["MES"].value_counts().sort_index().reset_index()
    por_mes.columns = ["Mes", "Incidentes"]
    por_mes["Mes_nombre"] = por_mes["Mes"].map(NOMBRE_MES)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=por_mes["Mes_nombre"], y=por_mes["Incidentes"],
        text=por_mes["Incidentes"].apply(lambda v: f"{v:,}"),
        textposition="outside",
        marker=dict(
            color=por_mes["Incidentes"],
            colorscale=[[0, "#aec6e8"], [1, C["azul"]]],
            showscale=False,
            line=dict(width=0),
        ),
        hovertemplate="<b>%{x}</b><br>%{y:,} incidentes<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        xaxis=dict(title="Mes del año 2020", gridcolor="#f0f0f0"),
        yaxis=dict(title="N.º de incidentes", gridcolor="#f0f0f0",
                   range=[0, por_mes["Incidentes"].max() * 1.18]),
        showlegend=False,
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(SOURCE, unsafe_allow_html=True)
    st.markdown("---")
    render_analisis(
        contexto=(
            "El dataset cubre 7 de los 8 primeros meses del año 2020 (junio ausente). "
            "El período coincide con la pandemia de COVID-19 y la cuarentena obligatoria "
            "decretada en Colombia el 25 de marzo, afectando la movilidad urbana."
        ),
        analisis=(
            "Febrero registra el pico más alto (3.567 incidentes). Caída sostenida en "
            "marzo–abril (2.738). Recuperación en mayo (3.174), nueva caída en julio "
            "(2.266). Variación entre mes más alto y más bajo: 37%."
        ),
        interpretacion=(
            "La caída de marzo–abril coincide directamente con el confinamiento obligatorio. "
            "La recuperación en mayo refleja la flexibilización de restricciones. "
            "La caída en julio puede asociarse a un rebrote de COVID-19."
        ),
        conclusion=(
            "La pandemia redujo los incidentes en cerca del 23% entre el pico (febrero) "
            "y el valle (abril). La actividad ciudadana y económica es el principal "
            "determinante del volumen de emergencias atendidas por la UAECOB."
        ),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GRAFICA 2 — Distribucion horaria
# ══════════════════════════════════════════════════════════════════════════════
elif grafica_sel == "g3":
    chart_header(
        "Grafica 2 · Distribucion temporal",
        "Incidentes por hora del día — UAECOB Bogotá 2020",
        "Patron horario de incidentes reportados entre las 00:00 y las 23:59 horas."
    )

    por_hora = df["HORA"].value_counts().sort_index()
    horas = list(range(24))
    vals  = [int(por_hora.get(h, 0)) for h in horas]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=horas, y=vals,
        mode="lines+markers",
        fill="tozeroy",
        fillcolor="rgba(42,181,160,0.12)",
        line=dict(color=C["teal"], width=2.5),
        marker=dict(size=6, color=C["teal"], line=dict(color="white", width=1.5)),
        hovertemplate="<b>%{x}:00 h</b><br>%{y:,} incidentes<extra></extra>",
    ))
    pico_h = int(np.argmax(vals))
    fig.add_annotation(
        x=pico_h, y=vals[pico_h],
        text=f"Pico maximo<br><b>{vals[pico_h]:,}</b>",
        showarrow=True, arrowhead=2, arrowcolor=C["teal"],
        ax=40, ay=-50,
        font=dict(size=11, color=C["teal"]),
        bgcolor="white", bordercolor=C["teal"], borderwidth=1,
    )
    fig.update_layout(
        **LAYOUT_BASE,
        xaxis=dict(title="Hora del dia", tickmode="linear", dtick=1, gridcolor="#f0f0f0"),
        yaxis=dict(title="N.º de incidentes", gridcolor="#f0f0f0"),
        showlegend=False,
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(SOURCE, unsafe_allow_html=True)
    st.markdown("---")
    render_analisis(
        contexto=(
            "El análisis horario permite identificar franjas de alta demanda y garantizar "
            "la disponibilidad de personal y unidades en momentos críticos. Es el insumo "
            "más directamente accionable para la planificación táctica del servicio."
        ),
        analisis=(
            "Dos picos bien definidos: 9h (1.943 incidentes) y 15h–16h (1.772). "
            "Actividad mínima entre 3h y 5h de la madrugada (177–209). La curva sube "
            "abruptamente desde las 6h con el inicio de la jornada urbana."
        ),
        interpretacion=(
            "La curva bimodal es característica de ciudades latinoamericanas con jornada "
            "laboral partida. El pico de 9h coincide con el inicio laboral e industrial; "
            "el de 15h–16h con la reactivación post-almuerzo y regreso a casa."
        ),
        conclusion=(
            "La demanda se concentra en dos franjas críticas: 8h–11h y 14h–17h. "
            "La UAECOB debe garantizar máxima disponibilidad en esas ventanas. "
            "Las madrugadas (2h–5h) permiten programar mantenimientos y relevos."
        ),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GRAFICA 3 — Tiempo de respuesta
# ══════════════════════════════════════════════════════════════════════════════
elif grafica_sel == "g5":
    chart_header(
        "Grafica 3 · Capacidad operativa",
        "Distribución del tiempo de respuesta — UAECOB Bogotá 2020",
        "Proporción de incidentes según rangos de tiempo de llegada (outliers > 120 min excluidos)."
    )

    tr = df["TR_limpio"].dropna()
    bins      = [0, 5, 10, 15, 20, 30, 60, 120]
    labels_tr = ["0–5 min","5–10 min","10–15 min","15–20 min","20–30 min","30–60 min","60–120 min"]
    conteos, _ = np.histogram(tr, bins=bins)
    pcts = conteos / conteos.sum() * 100
    colors_pie = [C["teal"], C["azul"], C["morado"], C["gris"], C["ambar"], C["naranja"], C["rojo"]]

    col_pie, col_tabla, col_hist = st.columns([1.3, 0.9, 1.4])

    with col_pie:
        fig_pie = go.Figure(go.Pie(
            labels=labels_tr,
            values=pcts,
            hole=0.44,
            marker=dict(colors=colors_pie, line=dict(color="white", width=2)),
            textinfo="percent",
            textfont=dict(size=11),
            hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>",
        ))
        fig_pie.update_layout(
            **LAYOUT_BASE,
            showlegend=False,
            height=320,
            annotations=[dict(
                text=f"Mediana<br><b>{tr.median():.1f} min</b>",
                x=0.5, y=0.5, font=dict(size=13, color=C["azul"]),
                showarrow=False,
            )],
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_tabla:
        st.markdown("##### Tabla de rangos")
        tabla_df = pd.DataFrame({
            "Rango": labels_tr,
            "%": [f"{p:.1f}%" for p in pcts],
            "Incidentes": [f"{c:,}" for c in conteos],
        })
        st.dataframe(tabla_df, use_container_width=True, hide_index=True, height=270)

    with col_hist:
        fig_hist = go.Figure(go.Histogram(
            x=tr, nbinsx=24,
            marker_color=C["verde"],
            opacity=0.85,
            hovertemplate="Tiempo: %{x} min<br>Incidentes: %{y:,}<extra></extra>",
        ))
        fig_hist.add_vline(
            x=tr.median(), line_dash="dash", line_color=C["rojo"],
            annotation_text=f"Mediana {tr.median():.1f} min",
            annotation_position="top right",
            annotation_font_color=C["rojo"],
        )
        fig_hist.update_layout(
            **LAYOUT_BASE,
            xaxis=dict(title="Minutos", gridcolor="#f0f0f0"),
            yaxis=dict(title="Incidentes", gridcolor="#f0f0f0"),
            showlegend=False,
            height=320,
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown(SOURCE, unsafe_allow_html=True)
    st.markdown("---")
    render_analisis(
        contexto=(
            "Muestra cómo se distribuyen los incidentes según el tiempo de llegada de la "
            f"unidad. Se excluyeron registros con tiempos superiores a 120 min. "
            f"Mediana general: {tr.median():.1f} min. Promedio: {tr.mean():.1f} min."
        ),
        analisis=(
            "El rango 5–10 minutos es el más frecuente (37,4%). El 55,2% se atendió en "
            "menos de 10 minutos. Solo el 4,6% tardó más de 30 minutos. "
            "Los tiempos de 60–120 min representan apenas el 0,6%."
        ),
        interpretacion=(
            "El tiempo de respuesta general de la UAECOB es satisfactorio. El 4,6% con "
            "tiempos superiores a 30 minutos merece atención especial, ya que en incendios "
            "activos ese tiempo puede ser determinante para el resultado de la intervención."
        ),
        conclusion=(
            "El desempeño es positivo, pero el 4,6% con tiempos > 30 min representa ~930 "
            "eventos en 8 meses. Se recomienda implementar alertas automáticas cuando el "
            "tiempo supere los 20 minutos para activar unidades de apoyo desde estaciones vecinas."
        ),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GRAFICA 4 — Tipo de servicio top 10
# ══════════════════════════════════════════════════════════════════════════════
elif grafica_sel == "g6":
    chart_header(
        "Grafica 4 · Composicion operativa",
        "Top 10 tipos de servicio más frecuentes — UAECOB Bogotá 2020",
        "Clasificación de cada atención según el tipo de servicio prestado por la UAECOB."
    )

    serv = df["SERVICIO"].value_counts().head(10).reset_index()
    serv.columns = ["Servicio", "Incidentes"]
    serv["Servicio"] = serv["Servicio"].apply(
        lambda s: s.split(". ", 1)[-1] if ". " in s else s
    )
    serv = serv.sort_values("Incidentes")

    fig = go.Figure(go.Bar(
        x=serv["Incidentes"], y=serv["Servicio"],
        orientation="h",
        text=serv["Incidentes"].apply(lambda v: f"{v:,}"),
        textposition="outside",
        marker=dict(
            color=serv["Incidentes"],
            colorscale=[[0, "#d7bde2"], [1, C["morado"]]],
            showscale=False,
            line=dict(width=0),
        ),
        hovertemplate="<b>%{y}</b><br>%{x:,} incidentes<extra></extra>",
    ))
    layout_g6 = {**LAYOUT_BASE, "margin": dict(t=20, b=40, l=220, r=80)}
    fig.update_layout(
        **layout_g6,
        xaxis=dict(title="N.º de incidentes", gridcolor="#f0f0f0",
                   range=[0, serv["Incidentes"].max() * 1.15]),
        yaxis=dict(title="", automargin=True),
        showlegend=False,
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(SOURCE, unsafe_allow_html=True)
    st.markdown("---")
    render_analisis(
        contexto=(
            "La UAECOB clasifica cada atención desde emergencias reales hasta actividades "
            "preventivas y falsas alarmas. Esta clasificación permite entender la naturaleza "
            "real de la carga operativa y la proporción de recursos destinados a cada tipo."
        ),
        analisis=(
            "Prevenciones (3.360) lideran, seguidas de Activaciones (2.792) y Continuaciones "
            "(2.296). Falsas Alarmas suman 2.249. Incidentes con animales (2.081) superan "
            "a los Incendios reales (719). Prevenciones + falsas alarmas + activaciones > 40%."
        ),
        interpretacion=(
            "Casi la mitad de los servicios no corresponde a emergencias activas, implicando "
            "un consumo significativo de recursos. Los incidentes con animales que superan a "
            "los incendios reflejan una carga diversificada más allá del rol tradicional."
        ),
        conclusion=(
            "La UAECOB destina ~40% de su capacidad a servicios no relacionados con emergencias "
            "activas. La alta proporción de falsas alarmas (11%) representa un costo evitable. "
            "Se recomienda revisar protocolos de activación y redistribuir la carga operativa."
        ),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GRAFICA 5 — Mapa coroplético + ranking por localidad
# ══════════════════════════════════════════════════════════════════════════════
elif grafica_sel == "g10":
    chart_header(
        "Grafica 5 · Distribucion territorial",
        "Incidentes por localidad de Bogotá D.C. — Mapa de calor",
        "El color más oscuro indica mayor concentración. Polígonos basados en límites administrativos oficiales."
    )

    metrica = st.radio(
        "Metrica a visualizar:",
        ["Incidentes", "Heridos", "Rescatados"],
        horizontal=True,
    )

    # ── Datos ──────────────────────────────────────────────────────────────
    resumen = (
        df.groupby("LOCALIDAD_L")
        .agg(
            Incidentes=("LOCALIDAD_L", "count"),
            Heridos=("TOTAL_HERIDOS", "sum"),
            Rescatados=("TOTAL_RESCATADOS", "sum"),
        )
        .reset_index()
        .rename(columns={"LOCALIDAD_L": "Localidad"})
    )
    resumen = resumen[resumen["Localidad"] != "FUERA D.C."].copy()

    PALETAS_MAPA = {
        "Incidentes": ["#e8f4fc", "#c6dff5", "#7db8e8", "#3a82c4", "#1a5ea8", "#0d2b5e"],
        "Heridos":    ["#fff0f0", "#fcd5d5", "#f5a0a0", "#e24b4b", "#b22020", "#7a0000"],
        "Rescatados": ["#e8faf4", "#b8edda", "#6dd4b0", "#1D9E75", "#14755a", "#0a4033"],
    }

    # ── Geodatos polígonos localidades ─────────────────────────────────────
    GEO = {
        "USAQUEN":        [(4.7563,-74.0467),(4.7534,-74.0007),(4.7008,-73.9978),(4.6683,-74.0149),(4.6635,-74.0508),(4.6941,-74.0622),(4.7294,-74.0505)],
        "CHAPINERO":      [(4.6934,-74.0508),(4.6683,-74.0149),(4.6317,-74.0471),(4.6185,-74.0595),(4.6295,-74.0807),(4.6529,-74.0776)],
        "SANTA FE":       [(4.6295,-74.0807),(4.6185,-74.0595),(4.5862,-74.0716),(4.5802,-74.0944),(4.5969,-74.0993),(4.6144,-74.0980)],
        "SAN CRISTOBAL":  [(4.5969,-74.0993),(4.5802,-74.0944),(4.5534,-74.0816),(4.5230,-74.1028),(4.5395,-74.1231),(4.5689,-74.1068),(4.5876,-74.1063)],
        "USME":           [(4.5395,-74.1231),(4.5230,-74.1028),(4.4929,-74.1117),(4.4417,-74.1421),(4.4237,-74.1817),(4.4691,-74.2028),(4.5197,-74.1634)],
        "TUNJUELITO":     [(4.5876,-74.1063),(4.5689,-74.1068),(4.5534,-74.1185),(4.5486,-74.1407),(4.5642,-74.1456),(4.5823,-74.1325)],
        "BOSA":           [(4.6457,-74.1567),(4.6338,-74.1697),(4.6027,-74.1879),(4.5941,-74.2073),(4.6072,-74.2162),(4.6326,-74.2013),(4.6567,-74.1873),(4.6592,-74.1694)],
        "KENNEDY":        [(4.6592,-74.1694),(4.6567,-74.1873),(4.6326,-74.2013),(4.6072,-74.2162),(4.5941,-74.2073),(4.5823,-74.1921),(4.5823,-74.1325),(4.6135,-74.1337),(4.6457,-74.1567)],
        "FONTIBON":       [(4.7003,-74.1095),(4.6916,-74.1046),(4.6592,-74.1694),(4.6457,-74.1567),(4.6135,-74.1337),(4.6071,-74.1299),(4.6338,-74.1199),(4.6634,-74.1072),(4.6896,-74.1029)],
        "ENGATIVA":       [(4.7294,-74.0505),(4.6941,-74.0622),(4.6677,-74.0855),(4.6520,-74.0942),(4.6338,-74.1197),(4.6634,-74.1072),(4.6896,-74.1029),(4.7003,-74.1095),(4.7294,-74.1021),(4.7422,-74.0789)],
        "SUBA":           [(4.7534,-74.0007),(4.7563,-74.0467),(4.7294,-74.0505),(4.7422,-74.0789),(4.7294,-74.1021),(4.7003,-74.1095),(4.7362,-74.1107),(4.7601,-74.1034),(4.7715,-74.0791),(4.7757,-74.0389)],
        "BARRIOS UNIDOS": [(4.6941,-74.0622),(4.6677,-74.0855),(4.6520,-74.0942),(4.6529,-74.0776),(4.6574,-74.0686),(4.6741,-74.0583)],
        "TEUSAQUILLO":    [(4.6677,-74.0855),(4.6529,-74.0776),(4.6295,-74.0807),(4.6144,-74.0980),(4.6188,-74.1138),(4.6338,-74.1197),(4.6520,-74.0942)],
        "LOS MARTIRES":   [(4.6295,-74.0807),(4.6144,-74.0980),(4.5969,-74.0993),(4.5969,-74.1112),(4.6071,-74.1113),(4.6188,-74.1138)],
        "ANTONIO NARINO": [(4.5969,-74.1112),(4.5969,-74.0993),(4.5876,-74.1063),(4.5823,-74.1325),(4.5921,-74.1320),(4.6071,-74.1113)],
        "PUENTE ARANDA":  [(4.6188,-74.1138),(4.6071,-74.1113),(4.5921,-74.1320),(4.5823,-74.1325),(4.6135,-74.1337),(4.6071,-74.1299),(4.6338,-74.1199),(4.6338,-74.1197)],
        "LA CANDELARIA":  [(4.5969,-74.0993),(4.5802,-74.0944),(4.5776,-74.0967),(4.5823,-74.1045),(4.5876,-74.1063)],
        "RAFAEL URIBE":   [(4.5534,-74.0816),(4.5230,-74.1028),(4.5395,-74.1231),(4.5486,-74.1407),(4.5534,-74.1185),(4.5689,-74.1068)],
        "CIUDAD BOLIVAR": [(4.5823,-74.1325),(4.5823,-74.1921),(4.5941,-74.2073),(4.5486,-74.2000),(4.4691,-74.2028),(4.4237,-74.1817),(4.4929,-74.1117),(4.5230,-74.1028),(4.5486,-74.1407),(4.5642,-74.1456)],
        "SUMAPAZ":        [(4.4417,-74.1421),(4.4929,-74.1117),(4.4237,-74.1817),(4.3800,-74.2200),(4.3500,-74.3000),(4.3200,-74.3500)],
    }

    CENTROS = {
        "USAQUEN":        (4.712, -74.023), "CHAPINERO":      (4.657, -74.059),
        "SANTA FE":       (4.600, -74.084), "SAN CRISTOBAL":  (4.562, -74.096),
        "USME":           (4.480, -74.128), "TUNJUELITO":     (4.572, -74.131),
        "BOSA":           (4.620, -74.187), "KENNEDY":        (4.630, -74.163),
        "FONTIBON":       (4.672, -74.147), "ENGATIVA":       (4.702, -74.115),
        "SUBA":           (4.748, -74.095), "BARRIOS UNIDOS": (4.671, -74.082),
        "TEUSAQUILLO":    (4.641, -74.093), "LOS MARTIRES":   (4.606, -74.101),
        "ANTONIO NARINO": (4.590, -74.115), "PUENTE ARANDA":  (4.614, -74.123),
        "LA CANDELARIA":  (4.596, -74.075), "RAFAEL URIBE":   (4.553, -74.110),
        "CIUDAD BOLIVAR": (4.509, -74.162), "SUMAPAZ":        (4.430, -74.220),
    }

    def normalizar(s):
        s = str(s).upper().strip()
        s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
        reemplazos = {
            "RAFAEL URIBE URIBE": "RAFAEL URIBE",
            "LOS MARTIRES": "LOS MARTIRES",
            "ANTONIO NARINO": "ANTONIO NARINO",
            "FONTIB": "FONTIBON",
            "ENGATIV": "ENGATIVA",
            "SAN CRISTOB": "SAN CRISTOBAL",
        }
        for k, v in reemplazos.items():
            if s.startswith(k): return v
        return s

    resumen["LOC_KEY"] = resumen["Localidad"].apply(normalizar)
    data_map = {row["LOC_KEY"]: int(row[metrica]) for _, row in resumen.iterrows()}
    total_metrica = sum(data_map.values())

    colorscale = PALETAS_MAPA[metrica]
    cmap = mcolors.LinearSegmentedColormap.from_list("custom", colorscale, N=256)
    vals_all = [data_map.get(loc, 0) for loc in GEO]
    vmin, vmax = min(vals_all), max(vals_all)

    def valor_a_color(v):
        t = 0.5 if vmax == vmin else (v - vmin) / (vmax - vmin)
        r, g, b, _ = cmap(t)
        return f"rgba({int(r*255)},{int(g*255)},{int(b*255)},0.88)"

    col_mapa, col_ranking = st.columns([1.3, 1])

    with col_mapa:
        fig_mapa = go.Figure()

        for loc_name, coords in GEO.items():
            val = data_map.get(loc_name, 0)
            pct = val / total_metrica * 100 if total_metrica > 0 else 0
            fill_color = valor_a_color(val)
            lats = [c[0] for c in coords] + [coords[0][0]]
            lons = [c[1] for c in coords] + [coords[0][1]]

            fig_mapa.add_trace(go.Scattergeo(
                lat=lats, lon=lons,
                mode="lines",
                fill="toself",
                fillcolor=fill_color,
                line=dict(color="white", width=1.5),
                hovertemplate=(
                    f"<b>{loc_name}</b><br>"
                    f"{metrica}: <b>{val:,}</b><br>"
                    f"Participacion: {pct:.1f}%<extra></extra>"
                ),
                showlegend=False,
            ))

            cx, cy = CENTROS.get(loc_name, (0, 0))
            short = (loc_name
                     .replace("ANTONIO NARINO","ANT.NARINO")
                     .replace("CIUDAD BOLIVAR","C.BOLIVAR")
                     .replace("BARRIOS UNIDOS","B.UNIDOS")
                     .replace("PUENTE ARANDA","PTE.ARANDA")
                     .replace("SAN CRISTOBAL","S.CRISTOBAL")
                     .replace("RAFAEL URIBE","R.URIBE"))
            fig_mapa.add_trace(go.Scattergeo(
                lat=[cx], lon=[cy],
                mode="text",
                text=[f"<b>{short}</b><br>{val:,}"],
                textfont=dict(size=8, color="#0d2b5e"),
                showlegend=False,
                hoverinfo="skip",
            ))

        # Colorbar
        n_cs = len(colorscale)
        fig_mapa.add_trace(go.Scattergeo(
            lat=[None], lon=[None], mode="markers",
            marker=dict(
                color=[vmin, vmax],
                colorscale=[[i/(n_cs-1) if n_cs > 1 else 0, c] for i, c in enumerate(colorscale)],
                showscale=True,
                cmin=vmin, cmax=vmax,
                colorbar=dict(
                    title=dict(text=f"N de<br>{metrica.lower()}", side="right", font=dict(size=10)),
                    thickness=14, len=0.75, tickfont=dict(size=9), x=1.01,
                ),
            ),
            showlegend=False, hoverinfo="skip",
        ))

        fig_mapa.update_geos(
            visible=False,
            lataxis_range=[4.43, 4.82],
            lonaxis_range=[-74.26, -73.98],
            bgcolor="#eaf4fb",
        )
        fig_mapa.update_layout(
            plot_bgcolor="#eaf4fb", paper_bgcolor="white",
            font_family="Inter",
            geo=dict(bgcolor="#eaf4fb"),
            margin=dict(t=30, b=10, l=0, r=60),
            height=600,
            showlegend=False,
            title=dict(
                text=f"<b>{metrica.upper()} POR LOCALIDAD — Bogotá D.C.</b><br>"
                     f"<sup>UAECOB · Ene–Ago 2020 · Total: {total_metrica:,}</sup>",
                x=0.5, xanchor="center",
                font=dict(size=13, color="#0d2b5e"),
            ),
        )
        st.plotly_chart(fig_mapa, use_container_width=True)

    with col_ranking:
        resumen_sorted = resumen.sort_values(metrica, ascending=False).reset_index(drop=True)
        resumen_sorted["LOC_KEY"] = resumen_sorted["Localidad"].apply(normalizar)
        resumen_sorted["Rank"] = resumen_sorted.index + 1
        resumen_sorted["Pct"]  = resumen_sorted[metrica] / resumen_sorted[metrica].sum() * 100

        fig_rank = go.Figure()
        fig_rank.add_trace(go.Bar(
            x=resumen_sorted[metrica],
            y=resumen_sorted["LOC_KEY"],
            orientation="h",
            text=resumen_sorted.apply(lambda r: f"{int(r[metrica]):,} ({r['Pct']:.1f}%)", axis=1),
            textposition="outside",
            marker=dict(
                color=resumen_sorted[metrica],
                colorscale=PALETAS_MAPA[metrica],
                showscale=False,
                line=dict(width=0),
            ),
            hovertemplate="<b>%{y}</b><br>%{x:,}<extra></extra>",
        ))
        for i, row in resumen_sorted.iterrows():
            fig_rank.add_annotation(
                x=0, y=row["LOC_KEY"],
                text=f"<b>{row['Rank']}.</b>",
                xref="x", yref="y",
                xanchor="right", showarrow=False,
                font=dict(size=9, color="#6b7280"),
                xshift=-4,
            )

        layout_rank = {**LAYOUT_BASE, "margin": dict(t=40, b=20, l=140, r=120)}
        fig_rank.update_layout(
            **layout_rank,
            title=dict(
                text=f"<b>Grafica 5 · {metrica} por Localidad</b><br>"
                     f"<sup>Total: {resumen_sorted[metrica].sum():,}</sup>",
                x=0.5, xanchor="center", font=dict(size=12, color="#0d2b5e"),
            ),
            xaxis=dict(visible=False, range=[0, resumen_sorted[metrica].max() * 1.45]),
            yaxis=dict(
                title="", automargin=True,
                categoryorder="array",
                categoryarray=list(reversed(resumen_sorted["LOC_KEY"].tolist())),
                tickfont=dict(size=9),
            ),
            showlegend=False,
            height=600,
        )
        st.plotly_chart(fig_rank, use_container_width=True)

    # Stats resumen
    top1   = resumen_sorted.iloc[0]
    bottom = resumen_sorted.iloc[-1]
    prom   = resumen_sorted[metrica].mean()

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(
            f'<div class="kpi-card" style="border-color:{C["azul"]}">'
            f'<div class="kpi-num" style="color:{C["azul"]};font-size:1.5rem">{int(top1[metrica]):,}</div>'
            f'<div class="kpi-label">Mayor · <b>{top1["LOC_KEY"]}</b></div></div>',
            unsafe_allow_html=True,
        )
    with sc2:
        st.markdown(
            f'<div class="kpi-card" style="border-color:{C["gris"]}">'
            f'<div class="kpi-num" style="color:{C["gris"]};font-size:1.5rem">{int(bottom[metrica]):,}</div>'
            f'<div class="kpi-label">Menor · <b>{bottom["LOC_KEY"]}</b></div></div>',
            unsafe_allow_html=True,
        )
    with sc3:
        st.markdown(
            f'<div class="kpi-card" style="border-color:{C["ambar"]}">'
            f'<div class="kpi-num" style="color:{C["ambar"]};font-size:1.5rem">{prom:,.1f}</div>'
            f'<div class="kpi-label">Promedio por localidad</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown(SOURCE, unsafe_allow_html=True)
    st.markdown("---")
    render_analisis(
        contexto=(
            "Los mapas coroplécticos muestran la distribución espacial de incidentes, heridos "
            "y rescatados en las 20 localidades de Bogotá D.C. El color más oscuro indica mayor "
            "concentración. Los polígonos corresponden a límites administrativos oficiales."
        ),
        analisis=(
            "Suba (2.293 incidentes, 85 heridos, 93 rescatados) lidera en las tres métricas. "
            "Kennedy y Engativá ocupan los siguientes lugares. Sumapaz registra los valores "
            "mínimos por su condición rural y distancia del casco urbano."
        ),
        interpretacion=(
            "La concentración en el norte y occidente de la ciudad refleja la mayor densidad "
            "poblacional y actividad industrial. Las localidades del sur como Ciudad Bolívar "
            "presentan tiempos de respuesta más altos pese a incidencia media-alta, "
            "evidenciando inequidad territorial en la cobertura del servicio."
        ),
        conclusion=(
            "Los tres indicadores muestran un patrón espacial consistente: norte y occidente "
            "concentran la mayor carga operativa. Se recomienda fortalecer la cobertura en el "
            "sur mediante subestaciones adicionales en Ciudad Bolívar, Rafael Uribe y Bosa."
        ),
    )


# ══════════════════════════════════════════════════════════════════════════════
# PIE DE PAGINA
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown(
    f"<div style='text-align:center;font-size:0.72rem;color:#9ca3af'>"
    f"Herramientas y Visualizacion de Datos · Proyecto 2 · "
    f"Fundacion Universitaria Los Libertadores · 2026 &nbsp;|&nbsp; "
    f"Dataset: {total:,} registros · Enero–Agosto 2020 &nbsp;|&nbsp; "
    f"Python · Streamlit · Plotly"
    f"</div>",
    unsafe_allow_html=True,
)
