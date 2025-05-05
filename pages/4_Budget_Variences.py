import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import visuals
from utils import show_logo

st.set_page_config(page_title="…", layout="wide")

# Affiche le logo cliquable, centré
show_logo(width=1200)

st.title("2025: Waterfall Analysis - Budget vs Forecast (Relative)")

@st.cache_resource
def get_connection():
    return sqlite3.connect(':memory:', check_same_thread=False)

@st.cache_data
def load_data(_conn):
    # Load fact table into in-memory SQLite
    df = pd.read_excel("./Data/df_fact.xlsx")
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['Date'] = pd.to_datetime(df['Date'])
    df['Revenue'] = (df['Volume'] * df['Unit Price']).round(0).astype(int)
    df.to_sql('Fact', _conn, index=False, if_exists='replace')
    # Load client dimension
    dim = pd.read_excel("./Data/final_client_dimension.xlsx")
    dim = dim.rename(columns={'Client Segment':'Segment'})[['Client','Segment']]
    dim.to_sql('DimClient', _conn, index=False, if_exists='replace')

# Initialize database connection and load data
conn = get_connection()
load_data(conn)

# Query Budget vs Forecast data for 2025
df_all = pd.read_sql_query(
    """
    SELECT f.Category,
           f.Subcategory,
           f.Client,
           d.Segment,
           SUM(CASE WHEN f.Scenario='Budget' THEN f.Volume * f.[Unit Price] ELSE 0 END) AS Budget,
           SUM(CASE WHEN f.Scenario='Forecast' THEN f.Volume * f.[Unit Price] ELSE 0 END) AS Forecast
    FROM Fact f
    LEFT JOIN DimClient d ON f.Client=d.Client
    WHERE f.Date >= '2025-01-01' AND f.Date < '2026-01-01'
      AND f.Scenario IN ('Budget','Forecast')
    GROUP BY f.Category, f.Subcategory, f.Client, d.Segment
    """,
    conn
)

# Function to plot relative waterfall
def plot_relative_waterfall(df, group_col, title):
    df_grp = df.groupby(group_col)[['Budget','Forecast']].sum()
    impacts = (df_grp['Forecast'] - df_grp['Budget']).sort_values(ascending=False)
    fig = go.Figure(go.Waterfall(
        x=impacts.index.tolist(),
        y=impacts.tolist(),
        measure=['relative'] * len(impacts),
        connector={'line':{'color':'rgb(63,63,63)'}}
    ))
    fig.update_layout(
        title=f'Relative Impact: Budget→Forecast by {title}',
        yaxis_title='Δ Revenue (€)',
        waterfallgap=0.4
    )
    st.plotly_chart(fig)

# Plot waterfall analyses
st.subheader("By Category")
plot_relative_waterfall(df_all, 'Category', 'Category')

st.subheader("By Subcategory")
plot_relative_waterfall(df_all, 'Subcategory', 'Subcategory')

st.subheader("By Client")
plot_relative_waterfall(df_all, 'Client', 'Client')

st.subheader("By Client Segment")
plot_relative_waterfall(df_all, 'Segment', 'Client Segment')

# --- Detailed table with conditional formatting ---
st.subheader("Detailed Budget vs Forecast Table")
# Compute deltas and percentages
df_table = df_all.copy()
df_table['Delta'] = df_table['Forecast'] - df_table['Budget']
df_table['Pct Change'] = df_table['Delta'] / df_table['Budget']

# Style with conditional formatting
dstyled = (
    df_table
    .style
    .format({
        'Budget': '€{0:,.0f}',
        'Forecast': '€{0:,.0f}',
        'Delta': '€{0:,.0f}',
        'Pct Change': '{0:.1%}'
    })
    .applymap(lambda v: 'color: green' if isinstance(v, (int, float)) and v > 0 else 'color: red', subset=['Delta', 'Pct Change'])
)

# Display styled table
st.write(dstyled)
