import streamlit as st
from classes.base_datos import BaseDatos
import json
import pandas as pd

with open("./datos/inventario.json", mode="r", encoding="utf-8") as file:
    data = json.load(file)

df = pd.DataFrame(data)

st.header("Restauración de la base de datos")

st.write("Se restaurará la base de datos a partir del archivo .json con los datos del inventario.")

st.dataframe(df.head())

if st.button("Restaurar Datos"):

    try:
        db = BaseDatos("./datos/inventario.db")
        conn = db.conn
        df.to_sql("productos", if_exists="replace", con = conn, index = False)
        conn.commit()

        # check if data were inserted into db
        cursor = db.cursor
        data = cursor.execute("select * from productos limit 10").fetchall()

        if len(data) == 10:
            st.success("Datos restaurados correctamente.")
    except Exception as e:
        st.warning(f"Error: {e}")