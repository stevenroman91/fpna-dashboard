# utils.py

import streamlit as st
from PIL import Image
from io import BytesIO
import base64

def show_logo(width: int = 150):
    """
    Affiche et centre le logo (images/logo.webp) ;
    lorsqu’on clique dessus, on revient à la home page ("/").
    """
    # 1) Charge et encode l’image
    img = Image.open("images/logo.webp")
    buf = BytesIO()
    img.save(buf, format="WEBP")
    b64 = base64.b64encode(buf.getvalue()).decode()

    # 2) Génère le HTML centré + lien vers "/"
    html = f"""
    <div style="text-align:center; margin-bottom:1rem;">
      <a href="/">
        <img src="data:image/webp;base64,{b64}" width="{width}" />
      </a>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
