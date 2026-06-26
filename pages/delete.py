from classes.inventario import Inventario
from classes.base_datos import BaseDatos
import pandas as pd
import streamlit as st
import time

db = BaseDatos("./datos/inventario.db")
conn = db.conn
inventario = Inventario(db)

df = pd.read_sql("select * from productos ;", conn)

brands = list(df.marca.unique())
categories = list( df.categoria.unique() )

st.set_page_config(layout="centered", initial_sidebar_state="collapsed")

# Inicialización al principio del script
if "select_all_active" not in st.session_state:
    st.session_state["select_all_active"] = False

if "editor_counter" not in st.session_state:
    st.session_state["editor_counter"] = 0

st.header("Eliminación de productos")

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
    brand_mask = df.marca == selected_brand

else:
    brand_mask = pd.Series(True, index = df.index)


if selected_category and selected_category != "Todas":
    category_mask = df.categoria == selected_category
else:
    category_mask = pd.Series(True, index = df.index)

filtered_df = (df[category_mask & brand_mask]
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

    filtered_df = (filtered_df[(filtered_df.precio >= min_price) & (filtered_df.precio <= max_price)]
                   .sort_values(["categoria", "marca", "nombre"])
                   .reset_index(drop = True)
    )

st.markdown("---")
st.header("Listado de productos:")

df = filtered_df.copy()

# Pre-poblar la columna según el flag persistente
df.insert(0, "Eliminar", st.session_state["select_all_active"])

current_key = f"editor_eliminar_{st.session_state['editor_counter']}"

df_edited = st.data_editor(
    df,
    column_config={
        "Eliminar": st.column_config.CheckboxColumn("Eliminar", default=False),
        "id": st.column_config.NumberColumn("ID", disabled=True),
        "nombre": st.column_config.TextColumn("Nombre", disabled=True),
        "marca": st.column_config.TextColumn("Marca", disabled=True),
        "categoria": st.column_config.TextColumn("Categoria", disabled=True),
        "precio": st.column_config.NumberColumn("Precio (€)", disabled=True, format="%.2f"),
        },
    column_order=["Eliminar", "id", "nombre", "marca", "categoria", "precio"],
    disabled=["id", "nombre", "marca", "categoria", "precio", "stock"],
    hide_index=True,
    key=current_key,
)

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("🗑️ Confirmar eliminación", type="primary"):
        products_to_be_removed_id_values = list(df_edited.loc[df_edited.Eliminar, "id"])
        try:
            for id in products_to_be_removed_id_values:
                inventario.eliminar_producto(id)
            st.session_state["select_all_active"] = False  # resetear flag
            st.success(f"{len(products_to_be_removed_id_values)} registros eliminados.")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.warning(f"Error: {e}")

with col2:
    def select_all_records():
        st.session_state["select_all_active"] = True
        st.session_state["editor_counter"] += 1  # fuerza remount
    
    st.button("Seleccionar todos", on_click=select_all_records)

with col3:
    def deselect_all_records():
        st.session_state["select_all_active"] = False
        st.session_state["editor_counter"] += 1  # fuerza remount
    
    st.button("Deseleccionar todos", on_click=deselect_all_records)