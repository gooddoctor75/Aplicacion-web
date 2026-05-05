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
import plotly.express as px
import plotly.graph_objects as go
import unicodedata

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="UAECOB · Dashboard 2020",
    page_icon="🚒",
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
    background: linear-gradient(180deg, #0d2b5e 0%, #1a4080 100%);
    border-right: 1px solid #ffffff18;
  }
  [data-testid="stSidebar"] * { color: #e8edf5 !important; }
  [data-testid="stSidebar"] .stRadio label { font-size: 0.88rem !important; }
  [data-testid="stSidebar"] .stRadio div[data-testid="stMarkdownContainer"] p {
    font-size: 0.82rem !important; color: #aec6e8 !important;
  }
  [data-testid="stSidebar"] hr { border-color: #ffffff30; }

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
  .kpi-label { font-size: 0.75rem; color: #6b7280; margin-top: 4px; letter-spacing: .3px; }

  /* ── Pill title ── */
  .chart-pill {
    display: inline-block;
    background: #3266ad;
    color: #fff !important;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: .8px;
    text-transform: uppercase;
    padding: 3px 12px;
    border-radius: 20px;
    margin-bottom: 6px;
  }
  .chart-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #0d2b5e;
    margin: 0 0 4px;
  }
  .chart-subtitle {
    font-size: 0.82rem;
    color: #6b7280;
    margin-bottom: 18px;
  }

  /* ── Analysis cards ── */
  .analysis-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 20px 0 10px;
  }
  .analysis-card {
    border-radius: 10px;
    padding: 16px;
    border-top: 3px solid;
  }
  .card-contexto      { background:#dbeafe; border-color:#3b82f6; }
  .card-analisis      { background:#fef3c7; border-color:#f59e0b; }
  .card-interpretacion{ background:#dcfce7; border-color:#22c55e; }
  .card-conclusion    { background:#ede9fe; border-color:#8b5cf6; }
  .card-icon  { font-size: 1.1rem; margin-bottom: 4px; }
  .card-label { font-size: 0.68rem; font-weight: 700; letter-spacing: .6px; text-transform: uppercase; margin-bottom: 6px; }
  .card-text  { font-size: 0.77rem; line-height: 1.55; color: #1e293b; }

  /* ── Source footer ── */
  .source-bar {
    font-size: 0.70rem;
    color: #9ca3af;
    border-top: 1px solid #e5e7eb;
    padding-top: 8px;
    margin-top: 4px;
  }

  /* ── Page header ── */
  .page-header {
    background: linear-gradient(135deg, #0d2b5e 0%, #1a5ea8 100%);
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
    color: white;
  }
  .header-title { font-size: 1.6rem; font-weight: 700; color: #fff; margin: 0; }
  .header-sub   { font-size: 0.82rem; color: #aec6e8; margin-top: 4px; }

  /* ── Divider ── */
  .section-sep { height: 2px; background: linear-gradient(90deg,#3266ad,transparent); border: none; margin: 28px 0 20px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DATOS
# ══════════════════════════════════════════════════════════════════════════════
def quitar_tildes(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", str(texto))
        if unicodedata.category(c) != "Mn"
    ).upper().strip()

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

@st.cache_data(show_spinner="⏳ Cargando datos del dataset UAECOB...")
def cargar_datos() -> pd.DataFrame:
    df = pd.read_csv(
        "incidentes-atendidos-por-uaecob-corte-31-agosto-2020.csv",
        encoding="latin1", sep=";", low_memory=False,
    )
    df["FECHA"]       = df["FECHA DEL EVENTO"].apply(parse_fecha)
    df["MES"]         = df["FECHA"].dt.month
    df["HORA"]        = pd.to_datetime(df["Hora reporte"], format="%H:%M:%S", errors="coerce").dt.hour
    df["DIA_SEM"]     = df["FECHA"].dt.dayofweek
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

df_raw = cargar_datos()
MESES_DISP = sorted(df_raw["MES"].dropna().unique())
LOCS_DISP  = sorted([l for l in df_raw["LOCALIDAD_L"].dropna().unique() if l != "FUERA D.C."])


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
GRAFICAS = {
    "📅 Gráfica 1 · Incidentes por mes":           "g1",
    "⏰ Gráfica 3 · Distribución horaria":          "g3",
    "⏱️ Gráfica 5 · Tiempo de respuesta":           "g5",
    "🗂️ Gráfica 6 · Tipo de servicio":              "g6",
    "🗺️ Gráfica 10 · Mapa de calor por localidad": "g10",
}

with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/"
        "Escudo_de_Bogot%C3%A1.svg/200px-Escudo_de_Bogot%C3%A1.svg.png",
        width=60,
    )
    st.markdown("## 🚒 UAECOB · Bogotá")
    st.markdown("**Dashboard de Incidentes**  \n*Enero – Agosto 2020*")
    st.divider()

    st.markdown("### 📊 Seleccionar gráfica")
    grafica_sel_label = st.radio(
        "", options=list(GRAFICAS.keys()), label_visibility="collapsed"
    )
    grafica_sel = GRAFICAS[grafica_sel_label]

    st.divider()
    st.markdown("### 🔽 Filtros globales")

    meses_sel = st.multiselect(
        "Mes", options=MESES_DISP, default=MESES_DISP,
        format_func=lambda m: NOMBRE_MES.get(m, str(m)),
    )
    locs_sel = st.multiselect(
        "Localidad", options=LOCS_DISP, default=LOCS_DISP,
    )
    st.divider()
    st.markdown(
        "<small>📁 Fuente: UAECOB · Datos Abiertos Bogotá<br>"
        "👨‍💻 J.C. Rojas · B.A. Sierra · 2026</small>",
        unsafe_allow_html=True,
    )

# ── Aplicar filtros ──────────────────────────────────────────────────────────
df = df_raw.copy()
if meses_sel:
    df = df[df["MES"].isin(meses_sel)]
if locs_sel:
    df = df[df["LOCALIDAD_L"].isin(locs_sel)]


# ══════════════════════════════════════════════════════════════════════════════
# ENCABEZADO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="page-header">
  <div class="header-title">🚒 Dashboard de Incidentes · UAECOB Bogotá D.C.</div>
  <div class="header-sub">
    Unidad Administrativa Especial Cuerpo Oficial de Bomberos &nbsp;·&nbsp;
    Periodo: Enero – Agosto 2020 &nbsp;·&nbsp;
    <a href="https://datosabiertos.bogota.gov.co/dataset/incidente-atendido-por-bomberos"
       style="color:#7ec8e3">Datos Abiertos Bogotá</a>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ─────────────────────────────────────────────────────────────────────
total      = len(df)
heridos    = int(df["TOTAL_HERIDOS"].sum())
rescatados = int(df["TOTAL_RESCATADOS"].sum())
tr_med     = df["TR_limpio"].median()
tr_str     = f"{tr_med:.1f} min" if pd.notna(tr_med) else "N/D"

k1, k2, k3, k4 = st.columns(4)
for col, num, label, color in [
    (k1, f"{total:,}",      "Total incidentes",          C["azul"]),
    (k2, f"{heridos:,}",    "Personas heridas",           C["rojo"]),
    (k3, f"{rescatados:,}", "Personas rescatadas",        C["verde"]),
    (k4, tr_str,            "Tiempo de respuesta mediano",C["ambar"]),
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
# HELPER: bloque de análisis en 4 tarjetas
# ══════════════════════════════════════════════════════════════════════════════
def render_analisis(contexto, analisis, interpretacion, conclusion):
    cards = [
        ("📌", "Contexto",       contexto,       "card-contexto",       "#1e40af"),
        ("🔍", "Análisis",       analisis,       "card-analisis",       "#92400e"),
        ("💡", "Interpretación", interpretacion, "card-interpretacion", "#166534"),
        ("✅", "Conclusión",     conclusion,     "card-conclusion",     "#5b21b6"),
    ]
    cols = st.columns(4)
    for col, (icon, label, text, css_class, color) in zip(cols, cards):
        with col:
            st.markdown(
                f'<div class="analysis-card {css_class}">'
                f'<div class="card-icon">{icon}</div>'
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

SOURCE = '<div class="source-bar">📁 Fuente: UAECOB · Datos Abiertos Bogotá · Periodo: Enero–Agosto 2020 (junio sin registros en el dataset)</div>'


# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICA 1 — Incidentes por mes
# ══════════════════════════════════════════════════════════════════════════════
if grafica_sel == "g1":
    chart_header(
        "Gráfica 1 · Evolución temporal",
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
# GRÁFICA 3 — Distribución horaria
# ══════════════════════════════════════════════════════════════════════════════
elif grafica_sel == "g3":
    chart_header(
        "Gráfica 3 · Distribución temporal",
        "Incidentes por hora del día — UAECOB Bogotá 2020",
        "Patrón horario de incidentes reportados entre las 00:00 y las 23:59 horas."
    )

    por_hora = df["HORA"].value_counts().sort_index()
    horas = list(range(24))
    vals  = [int(por_hora.get(h, 0)) for h in horas]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=horas, y=vals,
        mode="lines+markers",
        fill="tozeroy",
        fillcolor=f"rgba(42,181,160,0.15)",
        line=dict(color=C["teal"], width=2.5),
        marker=dict(size=6, color=C["teal"], line=dict(color="white", width=1.5)),
        hovertemplate="<b>%{x}:00 h</b><br>%{y:,} incidentes<extra></extra>",
    ))
    pico_h = int(np.argmax(vals))
    fig.add_annotation(
        x=pico_h, y=vals[pico_h],
        text=f"Pico máximo<br><b>{vals[pico_h]:,}</b>",
        showarrow=True, arrowhead=2, arrowcolor=C["teal"],
        ax=40, ay=-50,
        font=dict(size=11, color=C["teal"]),
        bgcolor="white", bordercolor=C["teal"], borderwidth=1,
    )
    fig.update_layout(
        **LAYOUT_BASE,
        xaxis=dict(title="Hora del día", tickmode="linear", dtick=1, gridcolor="#f0f0f0"),
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
# GRÁFICA 5 — Tiempo de respuesta
# ══════════════════════════════════════════════════════════════════════════════
elif grafica_sel == "g5":
    chart_header(
        "Gráfica 5 · Capacidad operativa",
        "Distribución del tiempo de respuesta — UAECOB Bogotá 2020",
        "Proporción de incidentes según rangos de tiempo de llegada de la unidad (outliers > 120 min excluidos)."
    )

    tr = df["TR_limpio"].dropna()
    bins   = [0, 5, 10, 15, 20, 30, 60, 120]
    labels_tr = ["0–5 min","5–10 min","10–15 min","15–20 min","20–30 min","30–60 min","60–120 min"]
    conteos, _ = np.histogram(tr, bins=bins)
    pcts = conteos / conteos.sum() * 100
    colors_pie = [C["teal"], C["azul"], C["morado"], C["gris"], C["ambar"], C["naranja"], C["rojo"]]

    col_pie, col_tabla, col_hist = st.columns([1.3, 0.9, 1.4])

    with col_pie:
        fig_pie = go.Figure(go.Pie(
            labels=labels_tr,
            values=pcts,
            hole=0.42,
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
            "unidad. Se excluyeron registros con tiempos superiores a 120 min. "
            f"Mediana general: {tr.median():.1f} min. Promedio: {tr.mean():.1f} min."
        ),
        analisis=(
            "El rango 5–10 minutos es el más frecuente (37,4%). El 55,2% se atendió en "
            "menos de 10 minutos. Solo el 4,6% tardó más de 30 minutos. "
            "Los tiempos de 60–120 min representan apenas el 0,6%."
        ),
        interpretacion=(
            "El tiempo de respuesta general de la UAECOB es satisfactorio. El 4,6% con "
            "tiempos superiores a 30 minutos merece atención especial ya que en incendios "
            "activos ese tiempo puede ser determinante para el resultado de la intervención."
        ),
        conclusion=(
            "El desempeño es positivo, pero el 4,6% con tiempos > 30 min representa ~930 "
            "eventos en 8 meses. Se recomienda implementar alertas automáticas cuando el "
            "tiempo supere los 20 minutos para activar unidades de apoyo desde estaciones vecinas."
        ),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICA 6 — Tipo de servicio top 10
# ══════════════════════════════════════════════════════════════════════════════
elif grafica_sel == "g6":
    chart_header(
        "Gráfica 6 · Composición operativa",
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
# GRÁFICA 10 — Mapa de calor por localidad
# ══════════════════════════════════════════════════════════════════════════════
elif grafica_sel == "g10":
    chart_header(
        "Gráfica 10 · Distribución territorial",
        "Incidentes, heridos y rescatados por localidad de Bogotá D.C.",
        "Comparación territorial de las tres métricas principales en las localidades de Bogotá."
    )

    metrica = st.radio(
        "Selecciona la métrica a visualizar:",
        ["Incidentes", "Heridos", "Rescatados"],
        horizontal=True,
    )

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

    PALETAS = {
        "Incidentes": [[0, "#cce5f6"], [1, C["azul"]]],
        "Heridos":    [[0, "#fde8e8"], [1, C["rojo"]]],
        "Rescatados": [[0, "#d1fae5"], [1, C["verde"]]],
    }

    col_bar, col_treemap = st.columns([1.2, 1])

    with col_bar:
        resumen_sorted = resumen.sort_values(metrica, ascending=True)
        fig_bar = go.Figure(go.Bar(
            x=resumen_sorted[metrica],
            y=resumen_sorted["Localidad"],
            orientation="h",
            text=resumen_sorted[metrica].apply(lambda v: f"{int(v):,}"),
            textposition="outside",
            marker=dict(
                color=resumen_sorted[metrica],
                colorscale=PALETAS[metrica],
                showscale=False,
                line=dict(width=0),
            ),
            hovertemplate="<b>%{y}</b><br>%{x:,}<extra></extra>",
        ))
        layout_bar = {**LAYOUT_BASE, "margin": dict(t=20, b=30, l=150, r=60)}
        fig_bar.update_layout(
            **layout_bar,
            xaxis=dict(title=metrica, gridcolor="#f0f0f0",
                       range=[0, resumen_sorted[metrica].max() * 1.18]),
            yaxis=dict(title="", automargin=True),
            showlegend=False,
            height=580,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_treemap:
        top8 = resumen.nlargest(8, metrica)
        fig_tree = px.treemap(
            top8,
            path=["Localidad"],
            values=metrica,
            color=metrica,
            color_continuous_scale=PALETAS[metrica],
            title=f"Top 8 localidades · {metrica}",
        )
        fig_tree.update_traces(
            textinfo="label+value",
            hovertemplate="<b>%{label}</b><br>%{value:,}<extra></extra>",
        )
        fig_tree.update_layout(
            **LAYOUT_BASE,
            height=580,
            coloraxis_showscale=False,
            title_font_size=13,
        )
        st.plotly_chart(fig_tree, use_container_width=True)

    top5 = resumen.nlargest(5, metrica)
    pct_top5 = top5[metrica].sum() / resumen[metrica].sum() * 100 if resumen[metrica].sum() > 0 else 0
    st.info(
        f"📍 **Insight:** Las 5 localidades con más {metrica.lower()} concentran "
        f"el **{pct_top5:.1f}%** del total del periodo seleccionado. "
        f"Lideran: **{', '.join(top5['Localidad'].tolist()[:3])}**."
    )
    st.markdown(SOURCE, unsafe_allow_html=True)

    st.markdown("---")
    render_analisis(
        contexto=(
            "Los mapas muestran la distribución espacial de incidentes, heridos y rescatados "
            "en las localidades de Bogotá D.C. El tono más oscuro indica mayor concentración. "
            "Se utilizan los límites administrativos oficiales de cada localidad."
        ),
        analisis=(
            "Suba (2.293 incidentes, 85 heridos, 93 rescatados) lidera en las tres métricas. "
            "Kennedy y Engativá ocupan los siguientes lugares. Sumapaz registra los valores "
            "mínimos por su condición rural y distancia del casco urbano."
        ),
        interpretacion=(
            "La concentración en el norte y occidente refleja la mayor densidad poblacional "
            "y actividad industrial. Las localidades del sur como Ciudad Bolívar y Usme "
            "presentan tiempos de respuesta más altos pese a una incidencia media-alta, "
            "evidenciando inequidad territorial."
        ),
        conclusion=(
            "Los tres indicadores muestran un patrón espacial consistente: norte y occidente "
            "concentran la mayor carga operativa. Se recomienda fortalecer la cobertura en el "
            "sur mediante subestaciones adicionales en Ciudad Bolívar, Rafael Uribe y Bosa."
        ),
    )


# ══════════════════════════════════════════════════════════════════════════════
# PIE DE PÁGINA
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown(
    f"<div style='text-align:center;font-size:0.75rem;color:#9ca3af'>"
    f"🎓 Herramientas y Visualización de Datos · Proyecto 2 · "
    f"Fundación Universitaria Los Libertadores · 2026 &nbsp;|&nbsp; "
    f"Dataset: {total:,} registros · Enero–Agosto 2020 &nbsp;|&nbsp; "
    f"Python · Streamlit · Plotly"
    f"</div>",
    unsafe_allow_html=True,
)
