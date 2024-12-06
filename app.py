import streamlit as st
import pandas as pd
import plotly.express as px
import pyodbc

# Configuración de la conexión a la base de datos
SERVER = '192.168.30.184'
DATABASE = 'ENGITASK'
USERNAME = 'Admin'
PASSWORD = 'Root123'
connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'

# Configuración de la página
st.set_page_config(page_title="Engitask Stats", layout="wide")
st.title("Engitask Stats")

# Cargar datos desde la base de datos
try:
    conn = pyodbc.connect(connectionString)

    SQL_QUERY = """
    SELECT 
        [Ingeniero], 
        [Puesto],
        [No#Proyecto],  
        [Semana],
        [Fecha],
        SUM(CAST([Total de Horas] AS FLOAT)) AS TotalHoras
    FROM 
        [ENGITASK].[dbo].[Planeador]
    GROUP BY 
        [Ingeniero], [Puesto], [No#Proyecto], [Semana], [Fecha]
    ORDER BY 
        [Semana] ASC;
    """
    df = pd.read_sql(SQL_QUERY, conn)
    conn.close()

    # Preprocesamiento de datos
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.month
    df['Año'] = df['Fecha'].dt.year

    # Filtros interactivos
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        selected_month = st.selectbox(
            "Seleccionar Mes",
            options=["Todos los Meses"] + sorted(df['Mes'].dropna().unique().tolist()),
            index=0
        )

    with col2:
        selected_year = st.selectbox(
            "Seleccionar Año",
            options=["Todos los Años"] + sorted(df['Año'].dropna().unique().tolist()),
            index=0
        )

    with col3:
        selected_engineer = st.selectbox(
            "Seleccionar Ingeniero",
            options=["Todos los Ing"] + sorted(df['Ingeniero'].unique().tolist()),
            index=0
        )

    with col4:
        selected_week = st.selectbox(
            "Seleccionar Semana",
            options=["Todas las Semanas"] + sorted(df['Semana'].unique().tolist()),
            index=0
        )

    # Filtrar datos
    filtered_df = df.copy()
    if selected_month != "Todos los Meses":
        filtered_df = filtered_df[filtered_df['Mes'] == selected_month]
    if selected_year != "Todos los Años":
        filtered_df = filtered_df[filtered_df['Año'] == selected_year]
    if selected_engineer != "Todos los Ing":
        filtered_df = filtered_df[filtered_df['Ingeniero'] == selected_engineer]
    if selected_week != "Todas las Semanas":
        filtered_df = filtered_df[filtered_df['Semana'] == selected_week]

    # Verificar si hay datos para mostrar
    if filtered_df.empty:
        st.warning("No hay datos para los filtros seleccionados.")
    else:
        # Layout de gráficos
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Total de Horas por Ingeniero")
            treemap_fig = px.treemap(
                filtered_df,
                path=['Ingeniero'],
                values='TotalHoras',
                color='TotalHoras',
                color_continuous_scale='Viridis',
                title='Total de Horas por Ingeniero'
            )
            st.plotly_chart(treemap_fig, use_container_width=True)

        with col2:
            st.subheader("Horas Totales por Puesto")
            bar_fig = px.bar(
                filtered_df.groupby('Puesto')['TotalHoras'].sum().reset_index(),
                x='Puesto',
                y='TotalHoras',
                color='TotalHoras',
                color_continuous_scale='Viridis',
                title='Horas Totales por Puesto'
            )
            st.plotly_chart(bar_fig, use_container_width=True)

        st.subheader("Horas Totales por Proyecto")
        project_fig = px.bar(
            filtered_df.groupby('No#Proyecto')['TotalHoras'].sum().reset_index(),
            x='No#Proyecto',
            y='TotalHoras',
            color='TotalHoras',
            color_continuous_scale='Viridis',
            title='Horas Totales por Proyecto'
        )
        st.plotly_chart(project_fig, use_container_width=True)

except pyodbc.Error as e:
    st.error(f"Error al conectar a la base de datos: {e}")
