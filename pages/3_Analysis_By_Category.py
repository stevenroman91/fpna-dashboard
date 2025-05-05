import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import visuals 
from utils import show_logo

st.set_page_config(page_title="Category Sales and Margin Analysis", layout="wide")

# Affiche le logo cliquable, centré
show_logo(width=1200)

st.title("Category Sales and Margin Distribution: Actual 2024 vs Forecast 2025")

@st.cache_resource
def get_connection():
    return sqlite3.connect(':memory:', check_same_thread=False)

@st.cache_data
def load_data(_conn):
    # Load unified fact table
    df = pd.read_excel("./Data/df_fact.xlsx")
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['Date'] = pd.to_datetime(df['Date'])
    df['Revenue'] = (df['Volume'] * df['Unit Price']).round(0).astype(int)
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
df_sales_act = df_act.groupby('Category', as_index=False)['Revenue'].sum().assign(Scenario='Actual 2024')
df_sales_fc  = df_fc.groupby('Category', as_index=False)['Revenue'].sum().assign(Scenario='Forecast 2025')

df_sales_dist = pd.concat([df_sales_act, df_sales_fc], ignore_index=True)
df_sales_dist['Pct'] = df_sales_dist.groupby('Scenario')['Revenue'].transform(lambda x: x / x.sum())

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
# Margin Distribution (amount)
# ----------------------
df_margin_act = df_act.assign(Margin=lambda d: d['Volume']*(d['Unit Price']-d['Unit Cost']))
df_margin_fc  = df_fc.assign(Margin=lambda d: d['Volume']*(d['Unit Price']-d['Unit Cost']))

df_margin_act = df_margin_act.groupby('Category', as_index=False)['Margin'].sum().assign(Scenario='Actual 2024')
df_margin_fc  = df_margin_fc.groupby('Category', as_index=False)['Margin'].sum().assign(Scenario='Forecast 2025')

df_margin_dist = pd.concat([df_margin_act, df_margin_fc], ignore_index=True)
df_margin_dist['Pct'] = df_margin_dist.groupby('Scenario')['Margin'].transform(lambda x: x / x.sum())

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
# Margin Rate by Category
# ----------------------
# 1. CA par catégorie
df_ca_act = df_act.groupby('Category', as_index=False)['Revenue'].sum().assign(Scenario='Actual 2024')
df_ca_fc  = df_fc.groupby('Category', as_index=False)['Revenue'].sum().assign(Scenario='Forecast 2025')
df_ca = pd.concat([df_ca_act, df_ca_fc], ignore_index=True)

# 2. Marge par catégorie
df_mg_act = df_act.assign(Margin=lambda d: d['Volume']*(d['Unit Price']-d['Unit Cost'])) \
                  .groupby('Category', as_index=False)['Margin'].sum() \
                  .assign(Scenario='Actual 2024')
df_mg_fc  = df_fc.assign(Margin=lambda d: d['Volume']*(d['Unit Price']-d['Unit Cost'])) \
                  .groupby('Category', as_index=False)['Margin'].sum() \
                  .assign(Scenario='Forecast 2025')
df_mg = pd.concat([df_mg_act, df_mg_fc], ignore_index=True)

# 3. Fusion CA + Marge
df_rate = pd.merge(df_ca, df_mg, on=['Category','Scenario'], how='inner', suffixes=('_CA','_MG'))

# 4. Calcul du taux de marge
df_rate['Margin Rate'] = df_rate['Margin'] / df_rate['Revenue']

fig_rate = px.bar(
    df_rate,
    x='Category',
    y='Margin Rate',
    color='Scenario',
    barmode='group',
    text='Margin Rate',
    title='Taux de Marge par Catégorie : Actual 2024 vs Forecast 2025',
    labels={'Margin Rate':'Taux de marge'}
)
fig_rate.update_traces(texttemplate='%{text:.2%}', textposition='inside')
fig_rate.update_yaxes(tickformat='.0%', title_text='Taux de marge')
st.plotly_chart(fig_rate)

# ----------------------
# Profitability by Customer Segment
# ----------------------
cust_dim = pd.read_excel("./Data/final_client_dimension.xlsx")
cust_dim = cust_dim.rename(columns={"Client Segment":"Segment"})

df_full = df.merge(cust_dim[['Client','Segment']], on='Client', how='left')
df_full['Margin'] = df_full['Volume'] * (df_full['Unit Price'] - df_full['Unit Cost'])

df_seg_act = df_full[(df_full['Scenario']=='Actual') & (df_full['Year']==2024)]
df_seg_fc  = df_full[(df_full['Scenario']=='Forecast') & (df_full['Year']==2025)]

df_seg_act = df_seg_act.groupby('Segment', as_index=False)['Margin'].sum().assign(Scenario='Actual 2024')
df_seg_fc  = df_seg_fc.groupby('Segment', as_index=False)['Margin'].sum().assign(Scenario='Forecast 2025')

df_seg_profit = pd.concat([df_seg_act, df_seg_fc], ignore_index=True)

fig_seg = px.bar(
    df_seg_profit,
    x='Segment',
    y='Margin',
    color='Scenario',
    barmode='group',
    text='Margin',
    title='Gross Profit by Customer Segment: Actual 2024 vs Forecast 2025',
    labels={'Margin':'Gross Profit (€)'}
)
fig_seg.update_traces(texttemplate='%{text:.3s}€', textposition='inside')
st.plotly_chart(fig_seg)
