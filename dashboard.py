import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.optimize import curve_fit
from PIL import Image
import psycopg2


st.set_page_config(page_title="Visualización Desempeño de compresores", layout="wide",)
alt.themes.enable("dark")


col1, col2, col3 = st.columns([1, 8, 1])  # Columnas para ubicar los logos

with col2:
    st.markdown("""<h1 style='text-align: center;'>Inicio</h1>""", unsafe_allow_html=True)
with col3:
    st.image(r"C:\UAO\ETL\Proyecto_ETL\Images\UAO-LOGO-.png", width=110)
