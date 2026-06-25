import sqlite3
from classes.inventario import Inventario
from classes.base_datos import BaseDatos
import pandas as pd
import streamlit as st
from datetime import date


db = BaseDatos("datos/inventario.db")
db.create_connection()

df = pd.read_sql("select * from productos", db.conn)

categories = sorted( list( df.categoria.unique() ) )


st.header("Insertar registro")
st.subheader("Añade información del nuevo producto")

with st.form("form_insertar", clear_on_submit=True):
    nombre = st.text_input("Nombre")
    marca = st.text_input("Marca")
    categoria = st.selectbox("Categoría", options = categories)
    precio = st.number_input("Precio (€)", min_value=0.0, step=0.01, format="%.2f")
    stock = st.number_input("Stock", min_value=0, step=1)
    especificaciones = st.text_area("Especificaciones")
    fecha_ingreso = st.date_input("Fecha de ingreso", value=date.today())

    submitted = st.form_submit_button("Insertar")

if submitted:
    if not nombre.strip() or not marca.strip():
        st.error("Nombre y marca son obligatorios.")
    else:
        datos = {
            "nombre": nombre.strip(),
            "marca": marca.strip(),
            "categoria": categoria,
            "precio": precio,
            "stock": int(stock),
            "especificaciones" : esoecificaciones,
            "fecha_ingreso": fecha_ingreso.isoformat(),  # "2026-06-25"
        }
        # aquí va la inserción (ver función abajo)
        db.insertar_producto(datos)
        st.success(f"'{datos['nombre']}' insertado correctamente.")


