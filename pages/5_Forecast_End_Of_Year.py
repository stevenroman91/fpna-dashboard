import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import visuals  # initialise votre template “green‑blue blend”
from utils import show_logo

st.set_page_config(page_title="…", layout="wide")

# Affiche le logo cliquable, centré
show_logo(width=1200)

st.title("2025 Forecast End-of-Year Analysis")

# 1) Connexion et chargement
@st.cache_resource
def get_connection():
    return sqlite3.connect(':memory:', check_same_thread=False)

@st.cache_data
def load_data(_conn):
    df = pd.read_excel("./Data/df_fact.xlsx")
    df = df.loc[:, ~df.columns.str.contains(r'^Unnamed')]
    df['Date']    = pd.to_datetime(df['Date'])
    df['Revenue'] = df['Volume'] * df['Unit Price']
    df['Cost']    = df['Volume'] * df['Unit Cost']
    df.to_sql("Fact", _conn, index=False, if_exists="replace")

conn = get_connection()
load_data(conn)

# 2) Charger les données Forecast 2025
df_fc = pd.read_sql_query("""
    SELECT Date, Country, Category, Volume, [Unit Price], [Unit Cost]
    FROM Fact
    WHERE Scenario = 'Forecast'
      AND Date >= '2025-01-01'
      AND Date <  '2026-01-01'
""", conn)
df_fc['Date'] = pd.to_datetime(df_fc['Date'])

# 3) Contrôles de filtre
st.sidebar.header("Assumptions")

# — Sélection multiple de pays (tout sélectionné par défaut)
countries = sorted(df_fc['Country'].unique())
selected_countries = st.sidebar.multiselect(
    "Pays",
    options=countries,
    default=countries
)

# — Sélection multiple de catégories (tout sélectionné par défaut)
categories = sorted(df_fc['Category'].unique())
selected_categories = st.sidebar.multiselect(
    "Catégories",
    options=categories,
    default=categories
)

# — Choix du scénario
scenario = st.sidebar.selectbox(
    "Scénario",
    ["Central", "Optimistic", "Pessimistic"]
)

# — Taux de croissance (%) de 0 % à 5 %
growth_pct = st.sidebar.slider(
    "Taux de croissance (%)",
    min_value=0.0, max_value=5.0, value=2.0, step=0.1,
    format="%.1f%%"
)
growth = growth_pct / 100.0

# 4) Déterminer le facteur à appliquer
if scenario == "Optimistic":
    factor = 1 + growth
elif scenario == "Pessimistic":
    factor = 1 - growth
else:
    factor = 1.0

# 5) Appliquer le filtre pays/catégorie et ajuster
df_base = df_fc.copy()
df_scen = df_fc.copy()

mask = (
    df_scen['Country'].isin(selected_countries) &
    df_scen['Category'].isin(selected_categories)
)
df_scen.loc[mask, 'Volume'] *= factor

# 6) Recalculer Revenue & Cost
for d in (df_base, df_scen):
    d['Revenue'] = d['Volume'] * d['Unit Price']
    d['Cost']    = d['Volume'] * d['Unit Cost']

# 7) Agrégation mensuelle
monthly_base = (
    df_base
    .groupby(pd.Grouper(key='Date', freq='M'))
    .agg(Revenue=('Revenue','sum'))
    .reset_index()
)
monthly_scen = (
    df_scen
    .groupby(pd.Grouper(key='Date', freq='M'))
    .agg(Revenue=('Revenue','sum'))
    .reset_index()
)

# 8) Filtrer la période d'affichage (04/2025 à 01/2026)
start, end = "2025-04-01", "2026-01-31"
monthly_base = monthly_base[
    (monthly_base['Date'] >= start) & (monthly_base['Date'] <= end)
]
monthly_scen = monthly_scen[
    (monthly_scen['Date'] >= start) & (monthly_scen['Date'] <= end)
]

# 9) Graphique comparatif
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=monthly_base['Date'], y=monthly_base['Revenue'],
    mode='lines+markers', name='Central'
))
fig.add_trace(go.Scatter(
    x=monthly_scen['Date'], y=monthly_scen['Revenue'],
    mode='lines+markers', name=scenario
))
fig.update_layout(
    title=f"2025 Sales Forecast – {scenario} ({growth_pct:.1f}% on selection)",
    xaxis_title="Date",
    yaxis_title="Sales (€)",
    legend_title="Scénarios"
)
st.plotly_chart(fig, use_container_width=True)

# 10) Totaux & marges
total_base_rev  = df_base['Revenue'].sum()
total_scen_rev  = df_scen['Revenue'].sum()
total_base_cost = df_base['Cost'].sum()
total_scen_cost = df_scen['Cost'].sum()

base_margin = (total_base_rev - total_base_cost) / total_base_rev
scen_margin = (total_scen_rev - total_scen_cost) / total_scen_rev
delta_rev_pct    = total_scen_rev / total_base_rev - 1
delta_margin_pct = scen_margin - base_margin

col1, col2 = st.columns(2)
col1.metric(
    label="Total Sales (Scenario)",
    value=f"€{total_scen_rev:,.0f}",
    delta=f"{delta_rev_pct:+.1%}".replace("%", "%%")
)
col2.metric(
    label="Margin (Scenario)",
    value=f"{scen_margin:.1%}".replace("%", "%%"),
    delta=f"{delta_margin_pct:+.1%}".replace("%", "%%")
)

