import sqlite3
from classes.inventario import Inventario
from classes.base_datos import BaseDatos
import pandas as pd
import streamlit as st


db = BaseDatos("datos/inventario.db")
db.create_connection()

all_data = pd.read_sql("select * from productos ;", db.conn)

brands = list(all_data.marca.unique())
categories = list( all_data.categoria.unique() )

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

st.header("Inventario de productos")

st.markdown("---")

st.subheader("Filtros")

col1, col2 = st.columns([1,1])

with col1:
    selected_category = st.selectbox(label = "Categoría",
                                    options = ["Todas"] + categories,
                                    key = "selected_category")

with col2:
    selected_brand = st.selectbox(label = "Marca",
                                options= ["Todas"] + brands,
                                key = "selected_brand")

if selected_brand and selected_brand != "Todas":
    brand_mask = all_data.marca == selected_brand

else:
    brand_mask = pd.Series(True, index = all_data.index)


if selected_category and selected_category != "Todas":
    category_mask = all_data.categoria == selected_category
else:
    category_mask = pd.Series(True, index = all_data.index)

filtered_df = (all_data[category_mask & brand_mask]
               .sort_values(["marca", "nombre"])
               .reset_index()
)


if len(filtered_df) == 0 :
    st.warning("La selección de filtros no generó ningún resultado.")
else:

    col1, col2, col3 = st.columns([2,1,1])

    with col1:
        # filtro de precios
        
        min_price, max_price = st.slider("Rango de precio",
                                        min_value=int(filtered_df.precio.min()) ,
                                        max_value = int(filtered_df.precio.max()),
                                        value = (0, round(filtered_df.precio.max()) ),
                                        step = 5,
                                        key = "price_range"
                                        )
        
    
    def reset_filters():
        st.session_state["selected_brand"] = "Todas"
        st.session_state["selected_category"] = "Todas" 

    def reset_price_range():
        st.session_state["price_range"] = (0, round(filtered_df.precio.max() ) )

    with col2:
            st.button("Limpiar filtros", on_click=reset_filters)

    with col3:
        st.button("Resetear rango precios", on_click= reset_price_range)

        filtered_df = filtered_df[(filtered_df.precio >= min_price) & (filtered_df.precio <= max_price)]

st.markdown("---")
st.header("Resultados:")
st.dataframe(filtered_df,
             column_order=["nombre", "marca", "categoria", "precio", "stock"],
             hide_index= True
             )

all_data.head()
# st.dataframe(all_data)∫