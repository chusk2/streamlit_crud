# CRUD Inventario con Streamlit

A multi-page Streamlit web app for managing a product inventory using SQLite as the database backend.

## Purpose

This project demonstrates how to build a full CRUD (Create, Read, Update, Delete) application with a web UI using Python, Streamlit, and SQLite — without any web framework boilerplate. The domain is a product inventory (electronics/tech items) with fields like name, brand, category, price, stock, and specs.

## Pages

| Page | Description |
|------|-------------|
| **Inventario** | Browse all products with filters by category, brand, and price range |
| **Añadir registro** | Form to insert a new product into the database |
| **Eliminar registros** | Interactive table with checkboxes to select and delete one or more products (includes select all / deselect all) |
| **Restaurar datos** | Restore the database from the bundled `inventario.json` backup file |

## Project Structure

```
crud_streamlit/
├── app.py                  # Entry point — defines the navigation between pages
├── pages/
│   ├── read.py             # READ: filterable product table
│   ├── create.py           # CREATE: insert new product form
│   ├── delete.py           # DELETE: checkbox-based batch deletion
│   └── restore_db.py       # Restore DB from JSON backup
├── classes/
│   ├── base_datos.py       # BaseDatos — SQLite connection wrapper
│   └── inventario.py       # Inventario — CRUD operations on the productos table
└── datos/
    ├── inventario.db       # SQLite database
    ├── inventario.json     # Seed / backup data
    └── inventario_backup.db
```

## Tech Stack

- **[Streamlit](https://streamlit.io/)** — UI and multi-page navigation
- **SQLite** (via `sqlite3`) — embedded relational database
- **Pandas** — data loading and filtering in the UI

## Getting Started

```bash
# Install dependencies
pip install streamlit pandas

# Run the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## Data Model

The `productos` table holds the inventory:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Auto-incremented identifier |
| `nombre` | TEXT | Product name |
| `marca` | TEXT | Brand |
| `categoria` | TEXT | Category |
| `precio` | REAL | Price (€) |
| `stock` | INTEGER | Units in stock |
| `especificaciones` | TEXT | Optional description/specs |
| `fecha_ingreso` | TEXT | Date added (ISO 8601) |
