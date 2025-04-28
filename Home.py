import streamlit as st
import visuals
from utils import show_logo

# Configuration de la page
st.set_page_config(
    page_title="FP&A Reallocation Analysis Dashboard",
    layout="wide"
)

# Affiche le logo cliquable, centré
show_logo(width=1200)

# Titre principal
st.title("FP&A Reallocation Analysis Dashboard")

st.write("Welcome to the financial planning and analysis (FP&A) dashboard.")

# Contenu textuel complet
st.markdown(
    """
    ## 📊 FP&A Reallocation Analysis Dashboard

    Welcome to the **Financial Planning & Analysis (FP&A)** dashboard, developed as part of a business audit initiative for the multi-country food retail operations of the company.

    ---

    ### 📦 Dataset Overview

    Before diving into the analysis, here’s a snapshot of the data included in this dashboard:

    - **20 unique clients**, segmented by region, cluster, and segment  
    - **5 account managers** overseeing client portfolios  
    - **4 product categories**: Beverages, Fresh Produce, Dry Goods, Frozen Food  
    - **12 subcategories** for granular product-level analysis  
    - **3 countries**: France, Spain, and Italy  
    - **Time coverage:**  
      - Full-year actuals for **2024**  
      - Full-year **2025 budget and forecast**  
      - Actuals for **Q1 2025 (January to March)**  
    - **Monthly granularity** for trend and seasonal analysis

    ---

    ### 🔍 What You'll Find Here

    - **📈 Multi-Year Performance Tracking**  
      Review actuals (2024), compare against 2025 budget and forecast, and monitor Q1 2025 results.

    - **📂 Category and Segment Insights**  
      Identify margin drivers and underperforming areas by product line and client segment.

    - **🔄 Scenario-Based Reallocation Modeling**  
      Simulate the impact of commercial decisions and growth assumptions on performance.

    ---

    ### Methodology

    All modeling and financial calculations were conducted in **Python**, including:

    - Data cleaning, transformation, and integration  
    - Calculation of key metrics:  
      – Sales, volumes, unit prices  
      – Unit costs and gross margins  
      – Margin rate, budget and forecast variances  
    - Scenario logic for forecasting and reallocation analysis

    The dashboard is built and deployed using **Streamlit**.

    ---

    ### 🎯 Dashboard Objectives

    - Monitor actual performance vs. plans  
    - Explain financial variances by country, category, and client  
    - Support quarterly reallocation and business reviews  
    - Provide decision-makers with interactive forecasting tools

    ---

    ### ❓ Key Questions This Dashboard Answers

    - Which countries contribute the most to sales?  
    - Which product category has the lowest margin?  
    - Which customer segments are the most profitable?  
    - What are the differences between actual and budget?  
    - What is the impact of applying +X% growth to Fresh Produce in France?  
    - What happens to overall margins if Frozen Food shows no growth?

    ---

    Use the **sidebar** to navigate between:  
    **Group Summary | Trends | Category Insights | Budget Variances | Forecast Simulation**

    This dashboard delivers **clarity, control, and strategic foresight** for financial planning.
    """,
    unsafe_allow_html=False
)
