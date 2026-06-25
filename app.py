import streamlit as st

pg = st.navigation([
    st.Page("pages/read.py", title="Inventario", icon="🔍"),
    st.Page("pages/create.py", title="Añadir registro", icon="📝"),
])
pg.run()