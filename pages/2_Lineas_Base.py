import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.optimize import curve_fit
from PIL import Image
import psycopg2


st.set_page_config(page_title="Visualización Desempeño de compresores", layout="wide",)# page_icon='C:\UAO\ETL\Proyecto_ETL\Images\icon.png')
alt.themes.enable("dark")

#Importar datos desde un SQL

####### Funciones para importar datos desde SQL y ajustar curvas ########
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
        df = df.resample('H').mean() # Resamplear los datos por hora

        conn.close()
        return df

    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return None
    
def modelo(x, a, b, c):
    return a*x ** (-b) + c # Definición del modelo a ajustar

# Ajuste de curvas para los compresores

def calculate_lb(data, x, y):
    df = data[[x, y]].dropna() # Eliminar filas con valores NaN

    popt, _ = curve_fit(modelo, df[x]/1000, df[y], maxfev=1000000,) # Ajustar el modelo a los datos
    
    # Calcular los valores ajustados
    y_fit = modelo(df[x]/1000, *popt)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[x], y=df[y], mode='markers', name='Datos Reales', marker_color = '#f2a852')) # Datos reales
    fig.add_trace(go.Scatter(x=df[x], y=y_fit, mode='markers', name=f'Modelo Ajustado {popt[0]:.4f}x^(-{popt[1]:.4f}) + {popt[2]:.4f}', marker_color = '#ed4e4e')) # Datos ajustados

    fig.update_layout(title=f'Ajuste: {x} vs {y}',
                        xaxis_title=x,
                        yaxis_title=y,
                        legend = dict(x=0.5, y=1),
                        width=800, height=600)
    print(f'Ajuste: {x} vs {y}')
    print(f'Parámetros del modelo: {popt}')
    print(f'Ecuación del modelo: {popt[0]:.4f}x^(-{popt[1]:.4f}) + {popt[2]:.4f}')
    
    return fig, popt 

def violin_plot(data, y1, y2):
    fig = go.Figure()
    fig.add_trace(go.Violin(y=data[y1], box_visible=True, marker_color = "#f2a852" , name=y1, points="all", ))
    fig.add_trace(go.Violin(y=data[y2], box_visible=True, marker_color = "#ed4e4e", name=y2, points="all", ))

    fig.update_layout(title='Comparación de KPI y Línea Base', height=600)
    return fig

col1, col2, col3 = st.columns([1, 8, 1])  # Columnas para ubicar los logos

with col2:
    st.markdown("""<h1 style='text-align: center;'>Líneas Base</h1>""", unsafe_allow_html=True)
with col3:
    st.image(r"C:\UAO\ETL\Proyecto_ETL\Images\UAO-LOGO-.png", width=110)


compresor_1 = get_data('compresor_1')
compresor_2 = get_data('compresor_2')

compresor_1 = compresor_1.resample('H').mean() # Resamplear los datos por hora
compresor_2 = compresor_2.resample('H').mean() # Resamplear los datos por hora

col1, col2 = st.columns([1, 1])  # Columnas para los compresores

fig_1, popt_1 = calculate_lb(compresor_1, 'Flujo Compresor 1 (SCFM)', 'KPI Compresor 1')
fig_2, popt_2 = calculate_lb(compresor_2, 'Flujo Compresor 2 (SCFM)', 'KPI Compresor 2')

with col1:
    st.plotly_chart(fig_1, use_container_width=True)
    st.plotly_chart(fig_2, use_container_width=True)
with col2:
    compresor_1['Línea Base'] = modelo(compresor_1['Flujo Compresor 1 (SCFM)']/1000, *popt_1)
    compresor_2['Línea Base'] = modelo(compresor_2['Flujo Compresor 2 (SCFM)']/1000, *popt_2)

    st.plotly_chart(violin_plot(compresor_1, 'KPI Compresor 1', 'Línea Base'), use_container_width=True)
    st.plotly_chart(violin_plot(compresor_2, 'KPI Compresor 2', 'Línea Base'), use_container_width=True)

