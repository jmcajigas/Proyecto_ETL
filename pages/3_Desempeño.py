import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.optimize import curve_fit
from PIL import Image
import psycopg2

def get_data(compresor):
    db_user = 'postgres'
    db_password = '1234'
    db_host = 'localhost'
    db_port = '5432'
    db_name = 'postgres'

    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )

        query = f"SELECT * FROM {compresor}"  # Asegúrate de que `compresor` es un nombre seguro
        df = pd.read_sql(query, conn)
        df.drop_duplicates(inplace=True)
        df.set_index('Fecha', inplace=True) 

        conn.close()
        return df

    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return None

def time_series(df, y,):

    unidad = "kW" if "Potencia" in y else "SCFM" if "Flujo" in y else "PSI" if "Presion" in y else "°C" if "Temperatura" in y else "kW/SCFM" 

    colores = ["#ed4e4e", "#f2a852", "#fdd175", "#eff0c7", "#c4e1f4", ]

    color = colores[0] if "Potencia" in y else colores[1] if "Flujo" in y else colores[2] if "Presion" in y else colores[3] if "Temperatura" in y else colores[4] if "Eficiencia" in y else None

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df[y], mode='lines', name='Real', marker_color=color))   
    fig.update_layout(title=y, xaxis_title="Fecha", yaxis_title=unidad)
    return fig


st.set_page_config(page_title="Visualización Desempeño de compresores", layout="wide",)
alt.themes.enable("dark")


col1, col2, col3 = st.columns([1, 8, 1])  # Columnas para ubicar los logos

with col2:
    st.markdown("""<h1 style='text-align: center;'>Desempeño</h1>""", unsafe_allow_html=True)
with col3:
    st.image(r"C:\UAO\ETL\Proyecto_ETL\Images\UAO-LOGO-.png", width=110)

with st.sidebar:   
    compresores = {'Compresor 1': 'compresor_1', 'Compresor 2': 'compresor_2'}
    seleccion = st.selectbox(label="Compresores", options=list(compresores.keys()), label_visibility="collapsed")
    compresor = compresores[seleccion]  # Mapea la selección al nombre real de la tabla
Compresor = get_data(compresor)  # Obtener datos del compresor seleccionado
numero = '1' if seleccion == 'Compresor 1' else '2'


with col2:
    st.plotly_chart(time_series(Compresor[-2000:], f'KPI Compresor {numero}'), use_container_width=True)
    st.plotly_chart(time_series(Compresor[-2000:], f'Potencia Compresor {numero} (kW)'), use_container_width=True)
    st.plotly_chart(time_series(Compresor[-2000:], f'Flujo Compresor {numero} (SCFM)'), use_container_width=True)
    st.plotly_chart(time_series(Compresor[-2000:], f'Presion Compresor {numero} (PSI)'), use_container_width=True)
    st.plotly_chart(time_series(Compresor[-2000:], f'Temperatura Compresor {numero} (°C)'), use_container_width=True)