"""
App 8 — CRUD completo con Flask.

Pieza final del recorrido: una aplicación Flask que ofrece la
funcionalidad CRUD completa sobre el inventario, usando las clases
`BaseDatos` e `Inventario` que diseñamos en la sesión del martes
(Semana 6).

- ### IDEAS CLAVE DEL DISEÑO DE LA APP ###
- Flask NO escribe SQL directamente.
- Flask habla únicamente con la API pública de `Inventario`.
- `Inventario` a su vez delega la persistencia en `BaseDatos`.
- Cada ruta es prácticamente un traductor HTTP → método de Inventario.

Rutas:
    GET  /                         → listado de productos (READ)
    GET  /producto/<id>            → ficha del producto (READ)
    GET  /producto/nuevo           → formulario para crear (CREATE - form)
    POST /producto/nuevo           → procesa creación
    GET  /producto/<id>/editar     → formulario de edición (UPDATE - form)
    POST /producto/<id>/editar     → procesa actualización
    POST /producto/<id>/eliminar   → elimina (DELETE)
"""

import os
from pathlib import Path

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, abort,
)

# Importamos las clases que construimos en la sesión del martes.
from classes.base_datos import BaseDatos
from classes.inventario import Inventario


# ---------- Configuración ----------
BASE_DIR = Path(__file__).resolve().parent
RUTA_JSON = BASE_DIR / "datos" / "inventario.json"

# `BaseDatos` siempre crea el archivo .db en `./datos/<nombre>.db`
# relativo al directorio desde el que se arranca la app. Por eso
# nos posicionamos en la raíz del proyecto antes de instanciarla,
# de modo que la BD acabe en `flask_tech/datos/inventario.db`.
os.chdir(BASE_DIR)


# ---------- Aplicación Flask ----------
app = Flask(
    __name__,
    # no es necesario, porque los directorios de
    # templates y static están donde se espera que estén
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)

# La secret key es necesaria para que funcionen los mensajes flash
# (Flask los firma criptográficamente al guardarlos en la sesión).
app.secret_key = "curso-python-semana6"

# ---------- Inventario: instancia única ----------
# Conectamos a la BD una sola vez al arrancar la app.
# Si la BD no existe todavía, BaseDatos la crea vacía y
# luego cargamos los productos desde el JSON.
db = BaseDatos("inventario")
inventario = Inventario(db)

# Si la tabla está vacía, la poblamos desde el JSON de partida.
if inventario.contar_registros() == 0:
    inventario.cargar_datos_desde_json(RUTA_JSON)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
# La API de Inventario no tiene métodos para obtener listas únicas
# de categorías y marcas. Como en el formulario de creación/edición
# necesitamos esos valores para los desplegables, los calculamos aquí
# una sola vez al arrancar, recorriendo todos los productos.

def obtener_categorias_y_marcas():
    """Devuelve (categorias_ordenadas, marcas_ordenadas) desde la BD."""
    registros = inventario.leer_todos_registros()
    # Mediante el uso de sqlite.Row (ver BaseDatos)
    # sqlite3 devuelve objetos Row, que permiten acceso "como" si
    # cada registro fuera un diccionario registro[clave]
    categorias = sorted({registro["categoria"] for registro in registros})
    marcas = sorted({registro["marca"] for registro in registros})
    
    return categorias, marcas


CATEGORIAS, MARCAS = obtener_categorias_y_marcas()  # caché inicial para el listado de index()


# ======================================================================
# READ — Listar y ver
# ======================================================================

@app.route("/")
def index():
    """Listado principal de productos, con filtro opcional por categoría."""
    
    # recarga las categorías por si se han creado nuevas
    CATEGORIAS, MARCAS = obtener_categorias_y_marcas()

    # select distinct categoria from products ;
    
    # <select id="categoria" name="categoria" onchange="this.form.submit()">
    # el template se encarga de obtener la categoría cuando
    # se selecciona una en la página de inicio
    categoria_filtro = request.args.get("categoria")

    if categoria_filtro:
        # suministra al template los productos filtrados por categoría
        productos = inventario.filtrar("categoria", categoria_filtro)
    else:
        # suministra al template todos los productos del inventario
        productos = inventario.leer_todos_registros()

    return render_template(
        "crud_listado.html",
        productos=productos,
        categorias=CATEGORIAS,
        categoria_filtro=categoria_filtro,
    )


@app.route("/producto/<int:id_producto>")
def ver_producto(id_producto):
    """Ficha completa de un producto."""
    producto = inventario.buscar_producto_por_id(id_producto)
    if not producto:
        abort(404)
    return render_template("crud_detalle.html", producto=producto)


# ======================================================================
# CREATE — Crear
# ======================================================================

@app.route("/producto/nuevo", methods=["GET", "POST"])
def crear_producto():
    if request.method == "POST":
        # Validación mínima
        nombre = request.form.get("nombre", "").strip()
        if not nombre:
            flash("El nombre es obligatorio.", "error")
            return redirect(url_for("crear_producto"))

        datos = {
            "nombre":           nombre,
            "marca":            request.form.get("marca", "").strip(),
            "categoria":        request.form.get("categoria", "").strip(),
            "precio":           request.form.get("precio", type=float),
            "stock":            request.form.get("stock", type=int),
            "especificaciones": request.form.get("especificaciones", "").strip(),
            "fecha_ingreso":    request.form.get("fecha_ingreso", "").strip(),
        }

        # `insertar_producto` no devuelve el id del nuevo registro,
        # así que lo recuperamos del cursor justo después de insertar
        # (lastrowid contiene el último id autoincrementado).
        inventario.insertar_producto(datos)
        nuevo_id = inventario.db.cursor.lastrowid

        # lanzar mensaje flash al crear un producto
        flash(f"Producto '{nombre}' creado con id {nuevo_id}.", "success")

        # patrón POST -> Redirect -> Get
        return redirect(url_for("ver_producto", id_producto=nuevo_id))

    # GET: mostramos el formulario (leemos BD para incluir categorías recién creadas)
    categorias, marcas = obtener_categorias_y_marcas()
    return render_template(
        "crud_formulario.html",
        producto=None,           # producto=None → modo creación
        categorias=categorias,
        marcas=marcas,
        accion=url_for("crear_producto"),
        titulo="Crear producto",
    )


# ======================================================================
# UPDATE — Editar
# ======================================================================

@app.route("/producto/<int:id_producto>/editar", methods=["GET", "POST"])
def editar_producto(id_producto):
    producto = inventario.buscar_producto_por_id(id_producto)
    if not producto:
        abort(404)

    if request.method == "POST":
        cambios = {
            "nombre":           request.form.get("nombre", "").strip(),
            "marca":            request.form.get("marca", "").strip(),
            "categoria":        request.form.get("categoria", "").strip(),
            "precio":           request.form.get("precio", type=float),
            "stock":            request.form.get("stock", type=int),
            "especificaciones": request.form.get("especificaciones", "").strip(),
            "fecha_ingreso":    request.form.get("fecha_ingreso", "").strip(),
        }

        inventario.actualizar_producto(id_producto, cambios)
        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for("ver_producto", id_producto=id_producto))

    categorias, marcas = obtener_categorias_y_marcas()
    return render_template(
        "crud_formulario.html",
        producto=producto,       # producto != None → modo edición
        categorias=categorias,
        marcas=marcas,
        accion=url_for("editar_producto", id_producto=id_producto),
        titulo=f"Editar: {producto['nombre']}",
    )


# ======================================================================
# DELETE — Eliminar
# ======================================================================

@app.route("/producto/<int:id_producto>/eliminar", methods=["POST"])
def eliminar_producto(id_producto):
    producto = inventario.buscar_producto_por_id(id_producto)
    if not producto:
        abort(404)

    nombre = producto["nombre"]
    inventario.eliminar_producto(id_producto)
    flash(f"Producto '{nombre}' eliminado.", "success")

    return redirect(url_for("index"))


# ======================================================================
# Manejadores de error
# ======================================================================

@app.errorhandler(404)
def page_not_found(error):
    return render_template("not_found_404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
