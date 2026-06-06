import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================

st.set_page_config(
    page_title="Dashboard de Inteligencia Comercial",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# SISTEMA DE COLOR Y DISEÑO
# =====================================================

C = {
    "bg":       "#0B1120",
    "surface":  "#111827",
    "border":   "#1F2D40",
    "primary":  "#2563EB",
    "accent":   "#38BDF8",
    "success":  "#10B981",
    "warning":  "#F59E0B",
    "danger":   "#EF4444",
    "text":     "#E2E8F0",
    "muted":    "#64748B",
    "white":    "#FFFFFF",
}

SEQ_BLUE = [
    [0.0,  "#0F2B6B"],
    [0.25, "#1D4ED8"],
    [0.5,  "#2563EB"],
    [0.75, "#60A5FA"],
    [1.0,  "#BAE6FD"],
]

CHART = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(
        family="'IBM Plex Sans', 'DM Sans', sans-serif",
        color=C["text"],
        size=12
    ),
    margin=dict(l=20, r=20, t=56, b=20),
    hoverlabel=dict(
        bgcolor=C["surface"],
        bordercolor=C["border"],
        font_color=C["text"],
        font_size=13,
    ),
)

AX = dict(
    gridcolor=C["border"],
    linecolor=C["border"],
    tickcolor=C["muted"],
    tickfont=dict(color=C["muted"], size=11),
    title_font=dict(color=C["muted"], size=12),
)

# =====================================================
# CSS GLOBAL
# =====================================================

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

  html, body, .stApp {{
    background-color: {C["bg"]};
    color: {C["text"]};
    font-family: 'IBM Plex Sans', sans-serif;
  }}

  /* Sidebar */
  section[data-testid="stSidebar"] {{
    background-color: {C["surface"]};
    border-right: 1px solid {C["border"]};
  }}
  section[data-testid="stSidebar"] * {{ color: {C["text"]} !important; }}

  /* Métricas */
  div[data-testid="metric-container"] {{
    background: {C["surface"]};
    border: 1px solid {C["border"]};
    border-radius: 10px;
    padding: 16px 20px 12px 20px;
    transition: border-color 0.2s;
  }}
  div[data-testid="metric-container"]:hover {{
    border-color: {C["primary"]};
  }}
  div[data-testid="metric-container"] label {{
    color: {C["muted"]} !important;
    font-size: 0.68rem !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 600;
  }}
  div[data-testid="stMetricValue"] {{
    color: {C["white"]} !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    font-family: 'IBM Plex Mono', monospace !important;
  }}

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {{
    background: {C["surface"]};
    border: 1px solid {C["border"]};
    border-radius: 10px;
    padding: 5px;
    gap: 3px;
  }}
  .stTabs [data-baseweb="tab"] {{
    background: transparent;
    border-radius: 7px;
    color: {C["muted"]};
    padding: 8px 20px;
    font-size: 0.82rem;
    font-weight: 500;
    letter-spacing: 0.03em;
    border: none;
  }}
  .stTabs [aria-selected="true"] {{
    background: {C["primary"]} !important;
    color: {C["white"]} !important;
  }}

  /* Alertas */
  div[data-testid="stAlert"] {{
    background: {C["surface"]};
    border: 1px solid {C["border"]};
    border-radius: 10px;
    font-size: 0.88rem;
  }}

  /* Tipografía */
  h1 {{
    color: {C["white"]} !important;
    font-weight: 800 !important;
    font-size: 1.9rem !important;
    letter-spacing: -0.02em;
  }}
  h2, h3 {{
    color: {C["text"]} !important;
    font-weight: 600 !important;
  }}
  hr {{ border-color: {C["border"]} !important; margin: 4px 0; }}
  code {{
    background: {C["surface"]};
    border: 1px solid {C["border"]};
    border-radius: 4px;
    color: {C["accent"]};
    padding: 1px 6px;
    font-family: 'IBM Plex Mono', monospace;
  }}

  /* Tags de sección */
  .tag {{
    display: inline-block;
    font-size: 0.63rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 4px;
    margin-bottom: 8px;
  }}
  .tag-analisis     {{ background: {C["primary"]}; color: white; }}
  .tag-interpreta   {{ background: {C["success"]}; color: white; }}
</style>
""", unsafe_allow_html=True)

# =====================================================
# CARGA DE DATOS
# =====================================================

@st.cache_data(show_spinner=False)
def cargar_datos():
    ventas_categoria = pd.read_parquet("data/marts/ventas_categoria.parquet")
    ventas_marca     = pd.read_parquet("data/marts/ventas_marca.parquet")
    conversion_marca = pd.read_parquet("data/marts/conversion_marca.parquet")
    funnel           = pd.read_parquet("data/marts/funnel.parquet")
    heatmap          = pd.read_parquet("data/marts/heatmap_hora_dia.parquet")
    actividad        = pd.read_parquet("data/marts/actividad_hora.parquet")
    return ventas_categoria, ventas_marca, conversion_marca, funnel, heatmap, actividad

with st.spinner("Cargando datos..."):
    ventas_categoria, ventas_marca, conversion_marca, funnel, heatmap, actividad = cargar_datos()


# =====================================================
# TRADUCCIÓN DE CATEGORÍAS
# =====================================================

traduccion_categorias = {
    "electronics":   "Electrónica",
    "appliances":    "Electrodomésticos",
    "computers":     "Computadores",
    "construction":  "Construcción",
    "accessories":   "Accesorios",
    "auto":          "Automóviles",
    "furniture":     "Muebles",
    "sport":         "Deportes",
    "kids":          "Niños",
    "medicine":      "Medicina",
    "country_yard":  "Jardín",
    "apparel":       "Ropa",
    "stationery":    "Papelería",
}

ventas_categoria["main_category"] = (
    ventas_categoria["main_category"].replace(traduccion_categorias)
)

# =====================================================
# PREPARACIÓN DEL FUNNEL (en español)
# =====================================================

funnel_es = funnel.copy()
funnel_es["event_type"] = funnel_es["event_type"].replace({
    "view":     "Visualizaciones",
    "cart":     "Carritos",
    "purchase": "Compras",
})

# =====================================================
# PREPARACIÓN DEL HEATMAP
# =====================================================

dias = {1:"Domingo", 2:"Lunes", 3:"Martes", 4:"Miércoles",
        5:"Jueves", 6:"Viernes", 7:"Sábado"}
heatmap["event_day"] = heatmap["event_day"].map(dias)

# =====================================================
# KPIs GLOBALES
# =====================================================

total_eventos    = int(funnel["count"].sum())
total_ingresos   = float(ventas_categoria["ingresos"].sum())
total_marcas     = int(ventas_marca["brand"].nunique())
total_categorias = int(ventas_categoria["main_category"].nunique())

visualizaciones = int(
    funnel.loc[funnel["event_type"] == "view", "count"].iloc[0]
)
compras = int(
    funnel.loc[funnel["event_type"] == "purchase", "count"].iloc[0]
)
conversion_global = (compras / visualizaciones) * 100

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    st.markdown(f"""
<div style='padding:4px 0 14px 0'>
  <div style='font-size:1.05rem;font-weight:700;color:#E2E8F0'>📊 Inteligencia Comercial</div>
  <div style='font-size:0.72rem;color:#64748B;margin-top:2px'>E-commerce · Octubre 2019</div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Resumen Global")
    st.metric("Conversión global",  f"{conversion_global:.2f}%")
    st.metric("Eventos totales",    f"{total_eventos:,.0f}")
    st.metric("Ingresos totales",   f"${total_ingresos:,.0f}")
    st.markdown("---")
    st.markdown("### 📁 Dataset")
    st.markdown("""
**E-commerce Clickstream**
Octubre 2019 · Kaggle

`42M` registros · `5.67 GB`
Procesado con **Apache Spark**
""")
    st.markdown("[🔗 Ver en Kaggle](https://www.kaggle.com/datasets/yashwant020/ecommerce-clickstream-dataset-5-27-gb)")
    st.markdown("---")
    st.markdown("### 👥 Autores")
    st.markdown("**Brayan Sierra**\nFundación Universitaria Los Libertadores · 2026")
    st.markdown("---")
    st.caption("Gerencia de Almacenamiento en Big Data · Corte 3")

# =====================================================
# ENCABEZADO
# =====================================================

st.markdown(f"""
<div style='padding:2px 0 6px 0'>
  <div style='font-size:0.68rem;font-weight:700;color:{C["primary"]};
       letter-spacing:0.15em;text-transform:uppercase;margin-bottom:4px'>
    Gerencia de Almacenamiento en Big Data · Actividad Final
  </div>
  <div style='font-size:1.9rem;font-weight:800;color:#F1F5F9;letter-spacing:-0.02em;line-height:1.15'>
    Dashboard de Inteligencia Comercial
    <span style='color:{C["primary"]}'>E-commerce</span>
  </div>
  <p style='color:{C["muted"]};font-size:0.88rem;margin-top:6px'>
    Análisis de comportamiento de usuarios, conversión e ingresos —
    procesamiento Big Data con PySpark · visualización con Streamlit & Plotly
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =====================================================
# KPIs PRINCIPALES
# =====================================================

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📊 Total Eventos",    f"{total_eventos:,.0f}")
c2.metric("💰 Ingresos",         f"${total_ingresos:,.0f}")
c3.metric("🏷 Marcas",           f"{total_marcas:,}")
c4.metric("📦 Categorías",       f"{total_categorias:,}")
c5.metric("🎯 Conversión",       f"{conversion_global:.2f}%")

st.markdown("---")

# =====================================================
# TABS
# =====================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛒 Embudo",
    "🛍 Categorías",
    "💰 Marcas",
    "⏰ Heatmap",
    "📈 Actividad",
])

# ─────────────────────────────────────────────
# TAB 1 — EMBUDO DE CONVERSIÓN
# ─────────────────────────────────────────────

with tab1:

    st.markdown('<div class="tag tag-analisis">Análisis</div>', unsafe_allow_html=True)
    st.markdown("""
Se analiza la distribución de los tres tipos de evento registrados en la plataforma:
**visualizaciones**, **carritos** y **compras**. El objetivo es cuantificar la eficiencia
del embudo de conversión e identificar en qué etapa se pierde mayor volumen de usuarios.

> **Elección del gráfico:** Barras horizontales para comparar magnitudes con proporciones muy
> desiguales (1 compra por cada ~55 vistas). El embudo complementa con porcentajes de caída.
""")
    st.markdown("---")

    col_izq, col_der = st.columns([3, 2], gap="large")

    with col_izq:
        # Barras horizontales con degradé de azul
        ev = funnel.copy()
        ev["label"] = ev["event_type"].replace({
            "view": "VISUALIZACIONES", "cart": "CARRITOS", "purchase": "COMPRAS"
        }).fillna(ev["event_type"].str.upper())
        ev = ev.sort_values("count", ascending=True)
        bar_hex = ["#93C5FD", "#2563EB", "#1E3A5F"][::-1][:len(ev)]

        fig1 = go.Figure()
        for i, (_, row) in enumerate(ev.iterrows()):
            fig1.add_trace(go.Bar(
                x=[row["count"]], y=[row["label"]],
                orientation="h",
                marker_color=bar_hex[i % len(bar_hex)],
                marker_line_width=0,
                text=f"  {row['count']:,.0f}",
                textposition="outside",
                textfont=dict(color=C["text"], size=12, family="IBM Plex Mono"),
                showlegend=False,
                hovertemplate=(
                    f"<b>{row['label']}</b><br>"
                    f"Eventos: {row['count']:,.0f}<br>"
                    f"Del total: {row['count']/total_eventos*100:.2f}%<extra></extra>"
                ),
            ))

        fig1.update_layout(
            **CHART,
            title=dict(
                text="<b>Visualización 1</b> · Distribución de tipos de evento<br>"
                     "<sup>Octubre 2019 — Comercio electrónico (flujo de clics)</sup>",
                font=dict(size=14, color=C["white"]),
            ),
            barmode="overlay",
            xaxis=dict(**AX, title="N.º de eventos", tickformat=".2s", showgrid=True),
            yaxis={
            **AX, "showgrid": False, "title": "","tickfont": dict(size=13, color=C["text"])
            },
            height=300,
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_der:
        # Funnel complementario
        fn_s = funnel_es.sort_values("count", ascending=False)
        fig_fn = go.Figure(go.Funnel(
            y=fn_s["event_type"], x=fn_s["count"],
            textposition="inside",
            textinfo="percent initial",
            marker=dict(
                color=["#2563EB", "#3B82F6", "#93C5FD"],
                line=dict(color=[C["bg"]] * 3, width=2),
            ),
            connector=dict(line=dict(color=C["border"], width=2, dash="dot")),
            hovertemplate="<b>%{y}</b><br>%{x:,.0f} eventos<extra></extra>",
        ))
        fig_fn.update_layout(
            **CHART,
            title=dict(text="Embudo de conversión",
                       font=dict(size=13, color=C["muted"])),
            height=300,
        )
        st.plotly_chart(fig_fn, use_container_width=True)

    r1, r2, r3 = st.columns(3)
    cart_count = int(funnel.loc[funnel["event_type"] == "cart", "count"].iloc[0]) \
                 if "cart" in funnel["event_type"].values else 0
    r1.metric("Vista → Carrito",
              f"{cart_count/visualizaciones*100:.2f}%" if cart_count else "N/A",
              f"{cart_count:,} al carrito")
    r2.metric("Carrito → Compra",
              f"{compras/cart_count*100:.2f}%" if cart_count else "N/A",
              f"{compras:,} compras")
    r3.metric("Vista → Compra", f"{conversion_global:.2f}%", "1 compra por ~55 vistas")

    st.markdown("---")
    st.markdown('<div class="tag tag-interpreta">Interpretación</div>', unsafe_allow_html=True)
    st.success(
        f"Se registraron **{visualizaciones:,.0f}** visualizaciones y **{compras:,.0f}** compras. "
        f"La tasa de conversión es de **{conversion_global:.2f}%**. "
        "La principal pérdida de usuarios ocurre entre la visualización del producto y la compra. "
        "Esto representa una oportunidad para optimizar promociones, descripciones de producto "
        "y la experiencia de navegación."
    )

# ─────────────────────────────────────────────
# TAB 2 — CATEGORÍAS
# ─────────────────────────────────────────────

with tab2:

    st.markdown('<div class="tag tag-analisis">Análisis</div>', unsafe_allow_html=True)
    st.markdown("""
Se analiza qué categorías principales generan mayores ingresos en la plataforma.
La distribución permite identificar los segmentos con mayor valor económico y
el grado de concentración del mercado.

> **Elección del gráfico:** Barras horizontales para el ranking de categorías
> (facilita lectura de etiquetas largas) y dona para la participación de mercado.
""")
    st.markdown("---")

    top_n_cat = st.slider("Mostrar top N categorías", 5, 15, 12, key="cat_sl")

    top_cat   = ventas_categoria.sort_values("ingresos", ascending=False).head(top_n_cat)
    top_cat_s = top_cat.sort_values("ingresos", ascending=True)

    col_c, col_d = st.columns([3, 2], gap="large")

    with col_c:
        fig2a = go.Figure(go.Bar(
            x=top_cat_s["ingresos"],
            y=top_cat_s["main_category"],
            orientation="h",
            marker=dict(
                color=top_cat_s["ingresos"],
                colorscale=SEQ_BLUE,
                line_width=0,
            ),
            text=[f"  ${v/1e6:.2f}M" for v in top_cat_s["ingresos"]],
            textposition="outside",
            textfont=dict(size=10, color=C["text"], family="IBM Plex Mono"),
            hovertemplate="<b>%{y}</b><br>Ingresos: $%{x:,.0f}<extra></extra>",
        ))
        fig2a.update_layout(
            **CHART,
            title=dict(
                text="<b>Visualización 2</b> · Categorías con mayor generación de ingresos<br>"
                     "<sup>Octubre 2019 — Comercio electrónico</sup>",
                font=dict(size=14, color=C["white"]),
            ),
            xaxis=dict(**AX, title="Ingresos (USD)", tickformat="$.2s", showgrid=True),
            yaxis={**AX,"title": "","showgrid": False,"tickfont": dict(size=11)
            },
            coloraxis_showscale=False,
            height=460,
        )
        st.plotly_chart(fig2a, use_container_width=True)

    with col_d:
        otros_ing = ventas_categoria["ingresos"].sum() - top_cat["ingresos"].sum()
        pie_df = pd.concat([
            top_cat[["main_category","ingresos"]].rename(columns={"main_category":"cat"}),
            pd.DataFrame([{"cat":"Otras","ingresos":otros_ing}])
        ])
        BLUES_L = ["#1E3A5F","#1D4ED8","#2563EB","#3B82F6","#60A5FA",
                   "#93C5FD","#BAE6FD","#BFDBFE","#DBEAFE","#EFF6FF",
                   "#1E40AF","#1E3A8A","#334155"]
        fig2b = go.Figure(go.Pie(
            labels=pie_df["cat"], values=pie_df["ingresos"],
            hole=0.60,
            marker=dict(
                colors=BLUES_L[:len(pie_df)],
                line=dict(color=C["bg"], width=2),
            ),
            textfont=dict(size=9, color=C["text"]),
            hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>",
        ))
        fig2b.add_annotation(
            text=f"<b>{total_categorias}</b><br>categorías",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=13, color=C["text"], family="IBM Plex Mono"),
        )
        fig2b.update_layout(
            **CHART,
            title=dict(text="Participación de mercado",
                       font=dict(size=13, color=C["muted"])),
            showlegend=True,
            legend=dict(font=dict(size=8, color=C["muted"]),
                        bgcolor="rgba(0,0,0,0)", x=1.0, y=0.5),
            height=460,
        )
        st.plotly_chart(fig2b, use_container_width=True)

    categoria_top = top_cat.iloc[0]["main_category"]
    ingreso_top   = top_cat.iloc[0]["ingresos"]
    conc_top3     = top_cat.head(3)["ingresos"].sum() / ventas_categoria["ingresos"].sum() * 100

    st.markdown("---")
    st.markdown('<div class="tag tag-interpreta">Interpretación</div>', unsafe_allow_html=True)
    st.success(
        f"La categoría líder es **{categoria_top}** con ingresos aproximados de **${ingreso_top:,.0f}**. "
        f"Las 3 categorías principales concentran el **{conc_top3:.1f}%** del total de ingresos. "
        "Las categorías líderes concentran la mayor parte del valor económico generado por la plataforma, "
        "permitiendo identificar segmentos prioritarios para inversión comercial y campañas publicitarias."
    )

# ─────────────────────────────────────────────
# TAB 3 — MARCAS
# ─────────────────────────────────────────────

with tab3:

    st.markdown('<div class="tag tag-analisis">Análisis</div>', unsafe_allow_html=True)
    st.markdown("""
Se identifican las marcas con mayor generación de ingresos y se contrasta
con su tasa de conversión, diferenciando marcas de **alto volumen** de marcas
con **alta eficiencia de ventas**.

> **Elección del gráfico:** Barras verticales para el ranking de ingresos,
> barras horizontales para la conversión, y scatter para revelar la relación entre ambas.
""")
    st.markdown("---")

    top_n_m = st.slider("Mostrar top N marcas", 5, 20, 15, key="marca_sl")

    top_brand = ventas_marca.sort_values("ingresos", ascending=False).head(top_n_m).copy()
    top_brand["brand"] = top_brand["brand"].str.title()
    top_brand["ingresos_m"] = top_brand["ingresos"] / 1_000_000

    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        n = len(top_brand)
        r_d, g_d, b_d = 0x1E/255, 0x3A/255, 0x5F/255
        r_l, g_l, b_l = 0x93/255, 0xC5/255, 0xFD/255
        bar_cols = []
        for i in range(n):
            t = 0.3 + 0.65 * (1 - i / max(n-1, 1))
            bar_cols.append("#{:02X}{:02X}{:02X}".format(
                int((r_d + t*(r_l-r_d))*255),
                int((g_d + t*(g_l-g_d))*255),
                int((b_d + t*(b_l-b_d))*255),
            ))

        fig3a = go.Figure()
        for i, (_, row) in enumerate(top_brand.iterrows()):
            fig3a.add_trace(go.Bar(
                x=[row["brand"]], y=[row["ingresos_m"]],
                marker_color=bar_cols[i], marker_line_width=0,
                text=f"${row['ingresos_m']:.2f}M",
                textposition="outside",
                textfont=dict(size=9, color=C["muted"]),
                showlegend=False,
                hovertemplate=(
                    f"<b>{row['brand']}</b><br>"
                    f"Ingresos: ${row['ingresos']:,.0f}<extra></extra>"
                ),
            ))
        fig3a.update_layout(
            **CHART,
            title=dict(
                text="<b>Visualización 3</b> · Top marcas por generación de ingresos<br>"
                     "<sup>Octubre 2019 — Comercio electrónico</sup>",
                font=dict(size=14, color=C["white"]),
            ),
            xaxis=dict(**AX, title="Marca", showgrid=False, tickangle=-35),
            yaxis=dict(**AX, title="Ingresos (Millones USD)", tickformat=".2f"),
            height=420,
        )
        st.plotly_chart(fig3a, use_container_width=True)

    with col_b:
        top_conv = conversion_marca.sort_values("conversion", ascending=False).head(top_n_m).copy()
        top_conv["brand"] = top_conv["brand"].str.title()
        top_conv_s = top_conv.sort_values("conversion", ascending=True)

        fig3b = go.Figure(go.Bar(
            x=top_conv["conversion"],
            y=top_conv_s["brand"],
            orientation="h",
            marker=dict(
                color=top_conv_s["conversion"],
                colorscale=SEQ_BLUE,
                line_width=0,
            ),
            text=[f"{v:.1f}%" for v in top_conv_s["conversion"]],
            textposition="outside",
            textfont=dict(size=10, color=C["muted"]),
            hovertemplate="<b>%{y}</b><br>Conversión: %{x:.2f}%<extra></extra>",
        ))
        fig3b.update_layout(
            **CHART,
            title=dict(text="Top marcas por tasa de conversión",
                       font=dict(size=14, color=C["white"])),
            xaxis=dict(**AX, title="Tasa de conversión (%)", showgrid=True),
            yaxis=dict(**AX, title="", showgrid=False),
            coloraxis_showscale=False,
            height=420,
        )
        st.plotly_chart(fig3b, use_container_width=True)

    # Scatter ingresos vs conversión
    merged = ventas_marca.merge(conversion_marca, on="brand", how="inner")
    merged["brand_fmt"] = merged["brand"].str.title()
    if "ingresos" in merged.columns and "conversion" in merged.columns:
        fig3c = px.scatter(
            merged.head(40),
            x="ingresos", y="conversion",
            text="brand_fmt", size="ingresos",
            color="conversion",
            color_continuous_scale=SEQ_BLUE,
            size_max=45,
            title="Relación: Ingresos vs Tasa de Conversión — Top 40 marcas",
        )
        fig3c.update_traces(
            textposition="top center",
            textfont=dict(size=8, color=C["muted"]),
            marker=dict(line=dict(width=1, color=C["bg"])),
            hovertemplate="<b>%{text}</b><br>Ingresos: $%{x:,.0f}<br>Conversión: %{y:.2f}%<extra></extra>",
        )
        fig3c.update_layout(
            **CHART,
            xaxis=dict(**AX, title="Ingresos (USD)", tickformat="$.2s"),
            yaxis=dict(**AX, title="Tasa de conversión (%)"),
            coloraxis_showscale=False,
            height=400,
        )
        st.plotly_chart(fig3c, use_container_width=True)

    mejor_marca  = top_brand.iloc[0]["brand"]
    ingresos_top = top_brand.iloc[0]["ingresos_m"]

    st.markdown("---")
    st.markdown('<div class="tag tag-interpreta">Interpretación</div>', unsafe_allow_html=True)
    st.success(
        f"La marca con mayor generación de ingresos es **{mejor_marca}** "
        f"con **${ingresos_top:,.2f} millones**. "
        "Las marcas líderes concentran una parte importante del valor económico. "
        "Identificar estas marcas permite enfocar estrategias de marketing, alianzas "
        "comerciales y promociones sobre los productos con mayor impacto en ventas."
    )

# ─────────────────────────────────────────────
# TAB 4 — HEATMAP HORA × DÍA
# ─────────────────────────────────────────────

with tab4:

    st.markdown('<div class="tag tag-analisis">Análisis</div>', unsafe_allow_html=True)
    st.markdown("""
Se estudia la intensidad de actividad de usuarios según la hora del día y el día
de la semana mediante un mapa de calor. Permite identificar franjas horarias y
días con mayor demanda para optimizar campañas y recursos tecnológicos.

> **Elección del gráfico:** Heatmap — visualización más eficiente para revelar
> patrones bidimensionales (hora × día) en una cuadrícula de valores.
""")
    st.markdown("---")

    orden_dias = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

    matriz = heatmap.pivot(
        index="event_day",
        columns="event_hour",
        values="count"
    ).reindex(orden_dias)

    fig4 = px.imshow(
        matriz,
        labels={"x":"Hora del día (UTC)", "y":"Día", "color":"Eventos"},
        aspect="auto",
        color_continuous_scale="Blues",
        title="<b>Visualización 4</b> · Mapa de calor — Actividad por hora y día<br>"
              "<sup>Octubre 2019 — Comercio electrónico (flujo de clics)</sup>",
    )
    fig4.update_layout(
        **CHART,
        xaxis=dict(**AX, title="Hora del día (UTC)", dtick=1),
        yaxis=dict(**AX, title="Día de la semana"),
        coloraxis_colorbar=dict(
    title=dict(text="USD"),
    tickfont=dict(size=11, color="#666666"),
    thickness=14,
        ),
        height=420,
    )
    st.plotly_chart(fig4, use_container_width=True)

    # Suma por día para gráfico secundario
    suma_dia = heatmap.groupby("event_day")["count"].sum().reindex(orden_dias).dropna()
    fig4b = go.Figure(go.Bar(
        x=suma_dia.index, y=suma_dia.values,
        marker=dict(
            color=suma_dia.values,
            colorscale=SEQ_BLUE,
            line_width=0,
        ),
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} eventos<extra></extra>",
    ))
    fig4b.update_layout(
        **CHART,
        title=dict(text="Eventos totales por día de la semana",
                   font=dict(size=13, color=C["muted"])),
        xaxis=dict(**AX, title="Día", showgrid=False),
        yaxis=dict(**AX, title="Total eventos", tickformat=".2s"),
        coloraxis_showscale=False,
        height=280,
    )
    st.plotly_chart(fig4b, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="tag tag-interpreta">Interpretación</div>', unsafe_allow_html=True)
    st.success(
        "El mapa de calor permite identificar los horarios y días con mayor volumen de actividad. "
        "Los periodos con mayor intensidad representan oportunidades para ejecutar campañas "
        "publicitarias y promociones con mayor impacto sobre la audiencia activa."
    )

# ─────────────────────────────────────────────
# TAB 5 — ACTIVIDAD POR HORA
# ─────────────────────────────────────────────

with tab5:

    st.markdown('<div class="tag tag-analisis">Análisis</div>', unsafe_allow_html=True)
    st.markdown("""
Se analiza la distribución de eventos a lo largo de las 24 horas del día.
El objetivo es identificar las horas pico para optimizar estrategias de marketing,
campañas promocionales y disponibilidad de recursos tecnológicos.

> **Elección del gráfico:** Área rellena con línea — comunica la tendencia continua
> y el volumen acumulado simultáneamente. La anotación del pico dirige la atención al dato clave.
""")
    st.markdown("---")

    actividad_s = actividad.sort_values("event_hour").copy()
    hora_pico   = int(actividad_s.loc[actividad_s["count"].idxmax(), "event_hour"])
    cnt_pico    = int(actividad_s["count"].max())
    promedio    = actividad_s["count"].mean()

    ventana = st.slider("Suavizado (media móvil, horas)", 1, 5, 1, key="smooth")
    actividad_s["smooth"] = actividad_s["count"].rolling(
        window=ventana, center=True, min_periods=1
    ).mean()

    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(
        x=actividad_s["event_hour"],
        y=actividad_s["smooth"],
        fill="tozeroy",
        fillcolor="rgba(37,99,235,0.15)",
        line=dict(color=C["accent"], width=2.5),
        mode="lines+markers",
        marker=dict(size=6, color=C["primary"],
                    line=dict(color=C["bg"], width=2)),
        hovertemplate="<b>%{x}:00 h</b><br>%{y:,.0f} eventos<extra></extra>",
        name="Eventos",
    ))

    fig5.add_annotation(
        x=hora_pico, y=cnt_pico,
        text=f"<b>Hora pico: {hora_pico}:00h</b><br>{cnt_pico/1e6:.2f}M eventos",
        showarrow=True, arrowhead=2,
        arrowcolor=C["danger"], arrowwidth=1.8,
        ax=60, ay=-50,
        font=dict(size=11, color=C["danger"]),
        bgcolor=C["surface"],
        bordercolor=C["danger"],
        borderwidth=1, borderpad=6,
    )

    fig5.add_hline(
        y=promedio, line_dash="dot",
        line_color=C["warning"], line_width=1.5,
        annotation_text=f"  Promedio: {promedio/1e6:.2f}M",
        annotation_font_color=C["warning"],
        annotation_font_size=10,
    )

    fig5.update_layout(
        **CHART,
        title=dict(
            text="<b>Visualización 5</b> · Actividad de usuarios por hora del día<br>"
                 "<sup>Octubre 2019 — Comercio electrónico (flujo de clics)</sup>",
            font=dict(size=14, color=C["white"]),
        ),
        xaxis=dict(**AX, title="Hora del día (UTC)",
                   tickmode="linear", tick0=0, dtick=1, showgrid=True),
        yaxis=dict(**AX, title="Número de eventos", tickformat=".2s"),
        showlegend=False,
        height=420,
    )
    st.plotly_chart(fig5, use_container_width=True)

    m1, m2, m3 = st.columns(3)
    hora_min = int(actividad_s.loc[actividad_s["count"].idxmin(), "event_hour"])
    cnt_min  = int(actividad_s["count"].min())
    m1.metric("⬆ Hora pico",    f"{hora_pico}:00 h", f"{cnt_pico/1e6:.2f}M eventos")
    m2.metric("⬇ Hora mínima",  f"{hora_min}:00 h",  f"{cnt_min/1e6:.2f}M eventos")
    m3.metric("∅ Promedio/hora", f"{promedio/1e6:.2f}M",
              f"σ {actividad_s['count'].std()/1e6:.2f}M")

    st.markdown("---")
    st.markdown('<div class="tag tag-interpreta">Interpretación</div>', unsafe_allow_html=True)
    st.success(
        f"La hora con mayor actividad registrada es las **{hora_pico}:00 horas UTC** "
        f"con **{cnt_pico/1e6:.2f}M eventos**. "
        "Conocer las horas pico permite optimizar estrategias de marketing, campañas "
        "promocionales y la disponibilidad de recursos tecnológicos en los momentos de mayor demanda."
    )

# =====================================================
# FUENTE DE DATOS
# =====================================================

st.markdown("---")

with st.expander("📚 Fuente de datos y metodología", expanded=False):
    st.markdown("""
**Dataset utilizado:**
Ecommerce Clickstream Dataset (5.67 GB)
[https://www.kaggle.com/datasets/yashwant020/ecommerce-clickstream-dataset-5-27-gb](https://www.kaggle.com/datasets/yashwant020/ecommerce-clickstream-dataset-5-27-gb)

**Metodología de procesamiento:**
- Carga y particionamiento con Apache Spark
- Limpieza: eliminación de nulos, duplicados y precios negativos
- Normalización de la columna `brand` (minúsculas + trim)
- Extracción de `event_hour` desde timestamp UTC
- Extracción de `main_category` desde jerarquía de categorías
- Exportación de marts analíticos en formato Parquet

**Entorno de ejecución:**
AMS Rizen 5600g · 32 GB RAM · Windows 11 · Apache Spark 3.x
""")

# =====================================================
# FOOTER
# =====================================================

st.markdown(f"""
<div style='display:flex;justify-content:space-between;align-items:center;
     padding:8px 0 2px 0;color:{C["muted"]};font-size:0.73rem;flex-wrap:wrap;gap:4px'>
  <span>📊 <b>Dashboard de Inteligencia Comercial</b> · E-commerce Clickstream</span>
  <span>Brayan Sierra · Los Libertadores · Junio 2026</span>
  <span>Apache Spark + Streamlit + Plotly</span>
</div>
""", unsafe_allow_html=True)
