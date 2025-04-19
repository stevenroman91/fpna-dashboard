# /pages/1_Group_Summary.py

import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import visuals
import calendar
from utils import show_logo

st.set_page_config(page_title="Group Summary", layout="wide")

# Affiche le logo centré et cliquable
show_logo(width=1200)

st.title("Group Summary: Monthly Sales Comparison")

# 1) Connexion & chargement en mémoire
@st.cache_resource
def get_connection():
    return sqlite3.connect(':memory:', check_same_thread=False)

@st.cache_data
def load_data(_conn):
    # Charge la table de faits
    df = pd.read_excel("./Data/df_fact.xlsx")
    df = df.loc[:, ~df.columns.str.contains(r"^Unnamed")]
    df['Date']    = pd.to_datetime(df['Date'])
    df['Revenue'] = df['Volume'] * df['Unit Price']
    df.to_sql("Fact", _conn, index=False, if_exists="replace")

    # Charge la dimension client pour avoir le segment
    dim = pd.read_excel("./Data/final_client_dimension.xlsx")
    dim = (
        dim
        .rename(columns={'Client Segment': 'Segment'})
        [['Client', 'Segment']]
    )
    dim.to_sql("DimClient", conn, index=False, if_exists="replace")

conn = get_connection()
load_data(conn)

# 2) Lecture et jointure de la table complète
df = pd.read_sql_query("""
    SELECT 
      f.Date,
      f.Country,
      f.Category,
      f.Client,
      d.Segment,
      f.Volume,
      f.[Unit Price],
      f.[Unit Cost],
      f.Revenue,
      f.Scenario
    FROM Fact f
    LEFT JOIN DimClient d ON f.Client = d.Client
""", conn)
df['Date'] = pd.to_datetime(df['Date'])

# 3) Ajout des colonnes temporelles
df['Year']      = df['Date'].dt.year
df['MonthNum']  = df['Date'].dt.month
df['MonthName'] = df['Date'].dt.strftime('%b')

# 4) Filtres utilisateur
st.sidebar.header("Filtres")

pays_list      = sorted(df['Country'].unique())
cats_list      = sorted(df['Category'].unique())
clients_list   = sorted(df['Client'].unique())
segments_list  = sorted(df['Segment'].dropna().unique())

selected_pays     = st.sidebar.multiselect("Pays",      options=pays_list,     default=pays_list)
selected_cats     = st.sidebar.multiselect("Catégories",options=cats_list,     default=cats_list)
selected_clients  = st.sidebar.multiselect("Clients",   options=clients_list,  default=clients_list)
selected_segments = st.sidebar.multiselect("Segments",  options=segments_list, default=segments_list)

# Appliquer les filtres
mask = (
    df['Country'].isin(selected_pays) &
    df['Category'].isin(selected_cats) &
    df['Client'].isin(selected_clients) &
    df['Segment'].isin(selected_segments)
)
df_filtered = df.loc[mask]

# 5) Figure 1 – ventes mensuelles Actual vs Budget/Forecast
dag = (
    df_filtered
    .groupby(['MonthNum','MonthName','Year','Scenario'], as_index=False)['Revenue']
    .sum()
)
df_rev = (
    dag
    .pivot_table(
        index=['MonthNum','MonthName'],
        columns=['Year','Scenario'],
        values='Revenue'
    )
    .sort_index()
    .reset_index()
)

months       = df_rev['MonthName']
rev_24_act   = df_rev.get((2024, 'Actual'),   pd.Series([0]*len(df_rev)))
rev_25_bud   = df_rev.get((2025, 'Budget'),   pd.Series([0]*len(df_rev)))
rev_25_fc    = df_rev.get((2025, 'Forecast'), pd.Series([0]*len(df_rev)))

fig1 = go.Figure()
fig1.add_trace(go.Bar(x=months, y=rev_24_act, name='Actual 2024', opacity=0.7))
fig1.add_trace(go.Bar(x=months, y=rev_25_bud, name='Budget 2025 (Q1)', opacity=0.7))
fig1.add_trace(go.Bar(x=months, y=rev_25_fc,  name='Forecast 2025',    opacity=0.7))
fig1.update_layout(
    title='Monthly Sales: Actual vs Budget/Forecast (2024–2025)',
    xaxis_title='Month',
    yaxis=dict(title='Revenue (€)'),
    barmode='group',
    legend_title='Series'
)
fig1.update_xaxes(tickformat='%b')
st.plotly_chart(fig1, use_container_width=True)

# 6) Figure 2 – marge brute mensuelle Actual 2024 vs Forecast 2025
df_margin = df_filtered.copy()
df_margin['MarginPct'] = ((df_margin['Unit Price'] - df_margin['Unit Cost'])
                          / df_margin['Unit Price']) * 100

margin_grp = (
    df_margin
    .assign(Weighted=lambda d: d['MarginPct'] * d['Revenue'])
    .groupby(['Year','MonthNum','Scenario'], as_index=False)
    .agg(Weighted=('Weighted','sum'), Revenue=('Revenue','sum'))
)
margin_grp['AvgMarginPct'] = margin_grp['Weighted'] / margin_grp['Revenue']

pt = margin_grp.pivot(index='MonthNum', columns=['Year','Scenario'], values='AvgMarginPct')
act_2024 = pt.get((2024,'Actual'),  pd.Series([None]*12))
fc_2025  = pt.get((2025,'Forecast'), pd.Series([None]*12))

months_full = [calendar.month_abbr[m] for m in range(1,13)]
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=months_full, y=act_2024.values, name='Actual 2024',  mode='lines+markers'))
fig2.add_trace(go.Scatter(x=months_full, y=fc_2025.values,  name='Forecast 2025', mode='lines+markers'))
fig2.update_layout(
    title='Monthly Gross Margin %: Actual 2024 vs Forecast 2025',
    xaxis_title='Month',
    yaxis_title='Margin %',
    legend_title='Scenario'
)
fig2.update_yaxes(tickformat='.1f%%')
st.plotly_chart(fig2, use_container_width=True)
