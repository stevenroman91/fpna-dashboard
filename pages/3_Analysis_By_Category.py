import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import visuals 
from utils import show_logo

st.set_page_config(page_title="…", layout="wide")

# Affiche le logo cliquable, centré
show_logo(width=1200)

st.title("Category Sales and Margin Distribution: Actual 2024 vs Forecast 2025")

@st.cache_resource
def get_connection():
    return sqlite3.connect(':memory:', check_same_thread=False)

@st.cache_data
def load_data(_conn):
    # Load unified fact table
    df = pd.read_excel("./Data/df_fact.xlsx")
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['Date'] = pd.to_datetime(df['Date'])
    df['Revenue'] = df['Volume'] * df['Unit Price']
    df.to_sql('Fact', _conn, index=False, if_exists='replace')

# Initialize database
conn = get_connection()
load_data(conn)

# Read data
df = pd.read_sql_query("SELECT * FROM Fact", conn)
df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year

# Filter scenarios
df_act = df[(df['Scenario'] == 'Actual') & (df['Year'] == 2024)]
df_fc  = df[(df['Scenario'] == 'Forecast') & (df['Year'] == 2025)]

# ----------------------
# Sales Distribution
# ----------------------
# Aggregate by Category
df_sales_act = df_act.groupby('Category', as_index=False)['Revenue'].sum().assign(Scenario='Actual 2024')
df_sales_fc  = df_fc.groupby('Category', as_index=False)['Revenue'].sum().assign(Scenario='Forecast 2025')

df_sales_dist = pd.concat([df_sales_act, df_sales_fc], ignore_index=True)
# Compute percentage share
df_sales_dist['Pct'] = df_sales_dist.groupby('Scenario')['Revenue'].transform(lambda x: x / x.sum())

# Plot 100% stacked bar with percent labels
fig_sales = px.bar(
    df_sales_dist,
    x='Scenario',
    y='Pct',
    color='Category',
    text='Pct',
    title='Sales Distribution by Category (100% stacked)',
    labels={'Pct':'% of Total Sales'}
)
fig_sales.update_traces(texttemplate='%{text:.2%}', textposition='inside')
fig_sales.update_yaxes(tickformat='.0%', title_text='Percentage of Sales')
st.plotly_chart(fig_sales)

# ----------------------
# Margin Distribution
# ----------------------
# Compute margin amount
df['Margin'] = df['Volume'] * (df['Unit Price'] - df['Unit Cost'])

# Filter for scenarios
df_margin_act = df_act.assign(Margin=df_act['Volume'] * (df_act['Unit Price'] - df_act['Unit Cost']))
df_margin_fc  = df_fc.assign(Margin=df_fc['Volume'] * (df_fc['Unit Price'] - df_fc['Unit Cost']))

# Aggregate by Category
df_margin_act = df_margin_act.groupby('Category', as_index=False)['Margin'].sum().assign(Scenario='Actual 2024')
df_margin_fc  = df_margin_fc.groupby('Category', as_index=False)['Margin'].sum().assign(Scenario='Forecast 2025')

df_margin_dist = pd.concat([df_margin_act, df_margin_fc], ignore_index=True)
# Compute percentage share
df_margin_dist['Pct'] = df_margin_dist.groupby('Scenario')['Margin'].transform(lambda x: x / x.sum())

# Plot 100% stacked bar for margin
fig_margin = px.bar(
    df_margin_dist,
    x='Scenario',
    y='Pct',
    color='Category',
    text='Pct',
    title='Margin Distribution by Category (100% stacked)',
    labels={'Pct':'% of Total Margin'}
)
fig_margin.update_traces(texttemplate='%{text:.2%}', textposition='inside')
fig_margin.update_yaxes(tickformat='.0%', title_text='Percentage of Margin')

st.plotly_chart(fig_margin)

# ----------------------
# Profitability by Customer Segment
# ----------------------
# Load customer dimension from final_client_dimension.xlsx
cust_dim = pd.read_excel("./Data/final_client_dimension.xlsx")
# Columns: Client, Client Segment
cust_dim = cust_dim.rename(columns={"Client Segment":"Segment"})
# Join with fact data
# fact df already has Client field matching

# Build full df for segment analysis
df_full = df.merge(cust_dim[['Client','Segment']], on='Client', how='left')

# Compute margin amount
df_full['Margin'] = df_full['Volume'] * (df_full['Unit Price'] - df_full['Unit Cost'])

# Filter scenarios and years
df_seg_act = df_full[(df_full['Scenario']=='Actual') & (df_full['Year']==2024)]
df_seg_fc  = df_full[(df_full['Scenario']=='Forecast') & (df_full['Year']==2025)]

# Aggregate margin by Segment
df_seg_act = df_seg_act.groupby('Segment', as_index=False)['Margin'].sum().assign(Scenario='Actual 2024')
df_seg_fc  = df_seg_fc.groupby('Segment', as_index=False)['Margin'].sum().assign(Scenario='Forecast 2025')

df_seg_profit = pd.concat([df_seg_act, df_seg_fc], ignore_index=True)

# Bar chart by customer segment
fig_seg = px.bar(
    df_seg_profit,
    x='Segment',
    y='Margin',
    color='Scenario',
    barmode='group',
    text='Margin',
    title='Gross Profit by Customer Segment: Actual 2024 vs Forecast 2025',
    labels={'Margin':'Gross Profit (€)'}
)

fig_seg.update_traces(
    texttemplate='%{text:.3s}€',
    textposition='inside'
)


st.plotly_chart(fig_seg)
