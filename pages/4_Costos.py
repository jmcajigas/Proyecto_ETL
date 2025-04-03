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
    
    
    return popt 

def ahorros_acumulados(df):
    fig = go.Figure()
    for i in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df[i].cumsum(), mode='lines', name=i))
    fig.update_layout(title="Consumos con respecto a Línea Base Acumulados", xaxis_title="Fecha", yaxis_title="(kWh)")

    return fig

def waterfall_chart(df):
    data = df.sum(axis=0).reset_index()
    data['Precio'] = data[0]*700
    #st.dataframe(data, use_container_width=True)
    fig = go.Figure(data=[
        go.Waterfall(
            x=data['index'],
            y=-data[0]/1000,
            measure=["relative", "relative", "total"],
            textposition="outside",
            text=data['Precio'].apply(lambda x: f"{x:.2f}").astype(str) + " COP",
            connector=dict(line=dict(color="black")),
            name="",
        )
    ])

    fig.update_layout(title="Ahorros por compresores", xaxis_title="Compresores", yaxis_title="(MWh)", showlegend=False)

    return fig
compresor_1 = get_data("compresor_1")
compresor_2 = get_data("compresor_2")

popt_1 = calculate_lb(compresor_1, "Flujo Compresor 1 (SCFM)", "Potencia Compresor 1 (kW)")
popt_2 = calculate_lb(compresor_2, "Flujo Compresor 2 (SCFM)", "Potencia Compresor 2 (kW)")

compresor_1['Línea Base'] = modelo(compresor_1["Flujo Compresor 1 (SCFM)"]/1000, *popt_1)/10000
compresor_2['Línea Base'] = modelo(compresor_2["Flujo Compresor 2 (SCFM)"]/1000, *popt_2)/10000

compresor_1['Ahorros (kW)'] = (compresor_1['KPI Compresor 1'] - compresor_1['Línea Base'])*compresor_1['Flujo Compresor 1 (SCFM)']
compresor_2['Ahorros (kW)'] = (compresor_2['KPI Compresor 2'] - compresor_2['Línea Base'])*compresor_2['Flujo Compresor 2 (SCFM)']

#st.dataframe(compresor_1[['Flujo Compresor 1 (SCFM)', 'Potencia Compresor 1 (kW)','KPI Compresor 1', 'Línea Base', 'Ahorros (kW)']], use_container_width=True)

st.set_page_config(page_title="Visualización Desempeño de compresores", layout="wide",)
alt.themes.enable("dark")

col1, col2, col3 = st.columns([1, 8, 1])  # Columnas para ubicar los logos
with col2:
    st.markdown("""<h1 style='text-align: center;'>Ahorros</h1>""", unsafe_allow_html=True)
with col3:
    st.image(r"C:\UAO\ETL\Proyecto_ETL\Images\UAO-LOGO-.png", width=110)


df_ahorros = pd.DataFrame()
df_ahorros['Compresor 1'] = compresor_1['Ahorros (kW)']
df_ahorros['Compresor 2'] = compresor_2['Ahorros (kW)']
df_ahorros['Ahorros Totales'] = df_ahorros.sum(axis=1)

col1, col2 = st.columns([1, 1])  # Columnas para los compresores
with col1:
    st.plotly_chart(ahorros_acumulados(df_ahorros), use_container_width=True)
with col2:
    st.plotly_chart(waterfall_chart(df_ahorros), use_container_width=True)
    

