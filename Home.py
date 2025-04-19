import streamlit as st
import visuals
from utils import show_logo

st.set_page_config(page_title="…", layout="wide")

# Affiche le logo cliquable, centré
show_logo(width=1200)

st.title("FP&A Reallocation Analysis Dashboard")

st.write("Welcome to the financial planning and analysis (FP&A) dashboard.")

st.markdown("""
This interactive application allows you to:
- **Have a Group summary** where you will find group total sales vs. budget, total margins and sales split by country. 
- **Analyze by category** comparing Actual vs Forecast by catetories from a sales point of view, a magin point of view.
- **Evaluate the Financial Impact** of reallocation decisions on Revenue and Gross Profit

It was developed as part of a business audit initiative to support management in:
- Reviewing past performance
- Monitoring variances
- Projecting sales for the upcoming quarter

Use the sidebar to navigate between sections and uncover insights that drive decision-making.
""")

