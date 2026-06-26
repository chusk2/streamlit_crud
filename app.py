import streamlit as st

pg = st.navigation([
    st.Page("pages/read.py", title="Inventario", icon="🔍"),
    st.Page("pages/create.py", title="Añadir registro", icon="📝"),
    st.Page("pages/delete.py", title = "Eliminar registros", icon="❌"),
    st.Page("pages/restore_db.py", title = "Restaurar datos", icon="💽")
])
pg.run()