import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import calendar
import visuals
from utils import show_logo

st.set_page_config(page_title="…", layout="wide")

# Affiche le logo cliquable, centré
show_logo(width=1200)

st.title("Group Summary: Monthly Sales Comparison")

@st.cache_resource
def get_connection():
    return sqlite3.connect(':memory:', check_same_thread=False)

@st.cache_data
def load_data(_conn):
    # Load raw data and push to in-memory SQL
    df = pd.read_excel("./Data/df_fact.xlsx")
    # Drop any unnamed index columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    # Parse Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    # Calculate revenue
    df['Revenue'] = df['Volume'] * df['Unit Price']
    # Write to SQL
    df.to_sql('Fact', _conn, index=False, if_exists='replace')

conn = get_connection()
load_data(conn)

# Read full table back and ensure proper types
df = pd.read_sql_query("SELECT * FROM Fact", conn)
# Convert Date from SQL back to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Extract Year, MonthNum, MonthName
df['Year'] = df['Date'].dt.year
df['MonthNum'] = df['Date'].dt.month
df['MonthName'] = df['Date'].dt.strftime('%b')

# Aggregate revenue by MonthNum, MonthName, Year, Scenario
dag = (
    df.groupby(['MonthNum', 'MonthName', 'Year', 'Scenario'], as_index=False)
      ['Revenue'].sum()
)

# Pivot revenue for plotting
df_rev = dag.pivot_table(
    index=['MonthNum', 'MonthName'],
    columns=['Year', 'Scenario'],
    values='Revenue'
)

# Sort by month number and reset index
df_rev = df_rev.sort_index().reset_index()

# Define x-axis categories
months = df_rev['MonthName']

# Prepare series for bars
rev_24_act = df_rev.get((2024, 'Actual'), pd.Series([0] * len(df_rev)))
rev_25_bud = df_rev.get((2025, 'Budget'), pd.Series([0] * len(df_rev)))
rev_25_fc  = df_rev.get((2025, 'Forecast'), pd.Series([0] * len(df_rev)))

# Build figure 1
fig1 = go.Figure()
fig1.add_trace(go.Bar(x=months, y=rev_24_act, name='Actual 2024', opacity=0.7))
fig1.add_trace(go.Bar(x=months, y=rev_25_bud, name='Budget 2025 (Q1)', opacity=0.7))
fig1.add_trace(go.Bar(x=months, y=rev_25_fc, name='Actual 2025 (Q1) - Forecast 2025 (Apr-Dec)', opacity=0.7))
fig1.update_layout(
    title='Monthly Sales: Actual vs Budget/Forecast (2024–2025)',
    xaxis_title='Month',
    yaxis=dict(title='Revenue (€)'),
    barmode='group',
    legend_title='Series'
)
fig1.update_xaxes(tickformat='%b')
st.plotly_chart(fig1)

# ---  Monthly Gross Margin %: Actual 2024 vs Forecast 2025 ---
# Calculate Revenue and MarginPct
df_margin = df.copy()
df_margin['Revenue'] = df_margin['Revenue']
df_margin['MarginPct'] = ((df_margin['Unit Price'] - df_margin['Unit Cost']) / df_margin['Unit Price']) * 100

# Extract Year and MonthNum
df_margin['Year'] = df_margin['Date'].dt.year
df_margin['MonthNum'] = df_margin['Date'].dt.month

# Weighted margin aggregation
df_margin['Weighted'] = df_margin['MarginPct'] * df_margin['Revenue']
margin_grp = (
    df_margin
    .groupby(['Year', 'MonthNum', 'Scenario'], as_index=False)
    .agg({'Weighted': 'sum', 'Revenue': 'sum'})
)
margin_grp['AvgMarginPct'] = margin_grp['Weighted'] / margin_grp['Revenue']

# Pivot and extract series for Actual 2024 and Forecast 2025
pt = margin_grp.pivot(
    index='MonthNum',
    columns=['Year', 'Scenario'],
    values='AvgMarginPct'
)
act_2024 = pt.get((2024, 'Actual'), pd.Series([None] * 12))
fc_2025 = pt.get((2025, 'Forecast'), pd.Series([None] * 12))

# Common x-axis months Jan-Dec
months = [calendar.month_abbr[m] for m in range(1, 13)]

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=months,
    y=act_2024.values,
    name='Actual 2024',
    mode='lines+markers'
))
fig2.add_trace(go.Scatter(
    x=months,
    y=fc_2025.values,
    name='Forecast 2025',
    mode='lines+markers'
))
fig2.update_layout(
    title='Monthly Gross Margin %: Actual 2024 vs Forecast 2025',
    xaxis_title='Month',
    yaxis_title='Margin %',
    legend_title='Scenario'
)
fig2.update_yaxes(tickformat='.1f%%')

st.plotly_chart(fig2)

# --- Figure 3: Sales by Country Over Time ---
query_country = '''
SELECT
    Date,
    Country,
    SUM(Volume * [Unit Price]) AS CountryRevenue
FROM Fact
WHERE Scenario = 'Actual'
GROUP BY Date, Country
ORDER BY Date;
'''
df_country = pd.read_sql_query(query_country, conn)
df_country['Date'] = pd.to_datetime(df_country['Date'])
fig3 = px.line(
    df_country,
    x='Date',
    y='CountryRevenue',
    color='Country',
    markers=True,
    title='Actual Sales by Country Over Time'
)
fig3.update_layout(
    xaxis_title='Date',
    yaxis_title='Sales (€)',
    legend_title='Country'
)
st.plotly_chart(fig3)

# --- Sales Distribution by Country ---
# Aggregate by Country
df_act = df[(df['Scenario']=='Actual') & (df['Year']==2024)]
df_fc  = df[(df['Scenario']=='Forecast') & (df['Year']==2025)]
rev_act_country = df_act.groupby('Country', as_index=False)['Revenue'].sum().assign(Scenario='Actual 2024')
rev_fc_country  = df_fc.groupby('Country', as_index=False)['Revenue'].sum().assign(Scenario='Forecast 2025')

df_country_dist = pd.concat([rev_act_country, rev_fc_country], ignore_index=True)

# Compute percentage share by Scenario for countries
df_country_dist['Pct'] = df_country_dist.groupby('Scenario')['Revenue'].transform(lambda x: x / x.sum())

# Plot 100% stacked bar chart by Country with percentage labels
fig_country = px.bar(
    df_country_dist,
    x='Scenario',
    y='Pct',
    color='Country',
    title='Sales Distribution by Country (100% stacked)',
    labels={'Pct':'% of Total Sales'},
    text= df_country_dist['Pct']
)
# Format and place text labels as percentages inside bars
fig_country.update_traces(
    texttemplate='%{text:.2%}',
    textposition='inside'
)
fig_country.update_yaxes(tickformat='.0%', title_text='Percentage of Sales')

st.plotly_chart(fig_country)

# ------------------------------------------------------------------
# Total Sales Bar Chart: Actual 2024, Budget 2025, Forecast 2025

# Total Sales Bar Chart: Actual 2024, Budget 2025, Forecast 2025

df_fact = pd.read_sql_query("SELECT Date, Volume, [Unit Price], Scenario FROM Fact", conn)
df_fact['Date'] = pd.to_datetime(df_fact['Date'])
df_fact['Year'] = df_fact['Date'].dt.year
# Compute revenue
df_fact['Revenue'] = df_fact['Volume'] * df_fact['Unit Price']

summary_totals = (
    df_fact[((df_fact['Year'] == 2024) & (df_fact['Scenario'] == 'Actual')) |
            ((df_fact['Year'] == 2025) & (df_fact['Scenario'].isin(['Budget', 'Forecast'])))]
    .groupby(['Year', 'Scenario'], as_index=False)['Revenue']
    .sum()
)

summary_totals['Label'] = summary_totals.apply(
    lambda r: 'Actual 2024' if (r['Year'] == 2024 and r['Scenario'] == 'Actual')
    else ('Budget 2025' if r['Scenario'] == 'Budget' else 'Forecast 2025'), axis=1
)

# Réorganiser pour avoir l'ordre chronologique
summary_totals = summary_totals.sort_values(by=['Year', 'Scenario'])

# Calculer les pourcentages d'évolution
actual_2024 = summary_totals[summary_totals['Label'] == 'Actual 2024']['Revenue'].values[0]
budget_2025 = summary_totals[summary_totals['Label'] == 'Budget 2025']['Revenue'].values[0]
forecast_2025 = summary_totals[summary_totals['Label'] == 'Forecast 2025']['Revenue'].values[0]

actual_to_budget_pct = ((budget_2025 - actual_2024) / actual_2024) * 100
budget_to_forecast_pct = ((forecast_2025 - budget_2025) / budget_2025) * 100

# Créer le graphique avec plus d'espace
fig_tot = px.bar(
    summary_totals,
    x='Label',
    y='Revenue',
    text='Revenue',
    title='Total Sales Comparison',
    labels={'Revenue': 'Total Sales (€)'},
    color='Label'
)

# Formater les montants et ajouter de l'espace pour éviter que le texte soit coupé
fig_tot.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')

# Ajouter les annotations pour les pourcentages d'évolution
fig_tot.add_annotation(
    x=0.5,  # Position entre les barres 0 et 1
    y=max(actual_2024, budget_2025) + 0.05 * max(summary_totals['Revenue']),
    text=f"{actual_to_budget_pct:+.1f}%",
    showarrow=True,
    arrowhead=2,
    arrowsize=1,
    arrowwidth=2,
    arrowcolor="#636363",
    ax=20,
    ay=-30
)

fig_tot.add_annotation(
    x=1.5,  # Position entre les barres 1 et 2
    y=max(budget_2025, forecast_2025) + 0.05 * max(summary_totals['Revenue']),
    text=f"{budget_to_forecast_pct:+.1f}%",
    showarrow=True,
    arrowhead=2,
    arrowsize=1,
    arrowwidth=2,
    arrowcolor="#636363",
    ax=20,
    ay=-30
)

# Mise en page améliorée
fig_tot.update_layout(
    yaxis_title='Sales (€)', 
    xaxis_title='Scenario',
    margin=dict(t=100, b=100, l=50, r=50),  # Augmenter les marges
    height=600,  # Augmenter la hauteur du graphique
    legend_title_text='',
    uniformtext_minsize=10,
    uniformtext_mode='hide'
)

# Ajuster l'axe Y pour éviter que le texte soit coupé
max_revenue = summary_totals['Revenue'].max()
fig_tot.update_yaxes(range=[0, max_revenue * 1.2])  # 20% d'espace supplémentaire au-dessus

st.plotly_chart(fig_tot, use_container_width=True)