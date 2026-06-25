import sqlite3
import json

class Inventario:
    # Atributo de clase: lista blanca de columnas permitidas.
    # Lo usamos para validar nombres de columna en filtros y actualizaciones.
    COLUMNAS_PERMITIDAS = {
        'nombre', 'marca', 'categoria', 'precio',
        'stock', 'especificaciones', 'fecha_ingreso'
    }

    # ---------------- Constructor ----------------
    def __init__(self, database):
        self.db = database
        self.db.create_connection()
        
        self._crear_tabla()
        print(f"Inventario conectado a '{self.db.name}'")

    # ---------------- Método interno ----------------
    def _crear_tabla(self):
        query = '''
            CREATE TABLE IF NOT EXISTS productos (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre           TEXT    NOT NULL,
                marca            TEXT    NOT NULL,
                categoria        TEXT    NOT NULL,
                precio           REAL    NOT NULL,
                stock            INTEGER NOT NULL,
                especificaciones TEXT,
                fecha_ingreso    TEXT
            )
        '''
        try:
            self.db.cursor.execute(query)
            self.db.commit()
        except sqlite3.Error as e:
            print(f'Error al crear la tabla: {e}')
            self.db.rollback()

    # ---------------- Auxiliar ----------------
    def listar_tablas(self):
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        tablas = self.db.cursor.execute(query).fetchall()
        # Excluimos la tabla interna sqlite_sequence
        return [t[0] for t in tablas if t[0] != 'sqlite_sequence']

    # ---------------- CREATE ----------------
    def insertar_producto(self, producto):
        query = '''
            INSERT INTO productos (nombre, marca, categoria, precio,
                                   stock, especificaciones, fecha_ingreso)
            VALUES (:nombre, :marca, :categoria, :precio,
                    :stock, :especificaciones, :fecha_ingreso)
        '''
        try:
            self.db.cursor.execute(query, producto)
            self.db.commit()
            print(f"Producto '{producto['nombre']}' insertado correctamente.")
        except sqlite3.Error as e:
            print(f'Error al insertar producto: {e}')
            self.db.rollback()

    def insertar_varios_productos(self, productos):
        query = '''
            INSERT INTO productos (nombre, marca, categoria, precio,
                                   stock, especificaciones, fecha_ingreso)
            VALUES (:nombre, :marca, :categoria, :precio,
                    :stock, :especificaciones, :fecha_ingreso)
        '''
        try:
            self.db.cursor.executemany(query, productos)
            self.db.commit()
            print(f'{len(productos)} productos insertados correctamente.')
        except sqlite3.Error as e:
            print(f'Error al insertar productos: {e}')
            self.db.rollback()

    def cargar_datos_desde_json(self, ruta_json):
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                productos = json.load(f)
            self.insertar_varios_productos(productos)
        except FileNotFoundError:
            print(f'Archivo no encontrado: {ruta_json}')
        except json.JSONDecodeError as e:
            print(f'Error al leer el JSON: {e}')

    # ---------------- READ ----------------
    def leer_todos_registros(self, limite=None):
        query = 'SELECT * FROM productos'
        if limite:
            query += f' LIMIT {limite}'
        try:
            return self.db.cursor.execute(query).fetchall()
        except sqlite3.Error as e:
            print(f'Error al leer productos: {e}')
            return []

    def contar_registros(self):
        query = 'SELECT COUNT(*) FROM productos'
        try:
            records_count = self.db.cursor.execute(query).fetchone()[0]
            return records_count
        except sqlite3.Error as e:
            print(f"Error al contar registros: {e}")
        
    def buscar_producto_por_id(self, id_producto):
        query = 'SELECT * FROM productos WHERE id = ?'
        try:
            return self.db.cursor.execute(query, (id_producto,)).fetchone()
        except sqlite3.Error as e:
            print(f'Error al buscar producto: {e}')
            return None

    def filtrar(self, columna, valor):
        if columna not in self.COLUMNAS_PERMITIDAS:
            print(f"Columna '{columna}' no permitida.")
            return []
        query = f'SELECT * FROM productos WHERE {columna} = ?'
        try:
            return self.db.cursor.execute(query, (valor,)).fetchall()
        except sqlite3.Error as e:
            print(f'Error al filtrar: {e}')
            return []

    # ---------------- UPDATE ----------------
    def actualizar_producto(self, id_producto, campos):
        for col in campos:
            if col not in self.COLUMNAS_PERMITIDAS:
                print(f"Columna '{col}' no permitida.")
                return

        asignaciones = ', '.join(f'{col} = :{col}' for col in campos)
        query = f'UPDATE productos SET {asignaciones} WHERE id = :id'
        parametros = {**campos, 'id': id_producto}

        try:
            self.db.cursor.execute(query, parametros)
            self.db.commit()
            if self.db.cursor.rowcount > 0:
                print(f'Producto {id_producto} actualizado.')
            else:
                print(f'No se encontró producto con id {id_producto}.')
        except sqlite3.Error as e:
            print(f'Error al actualizar: {e}')
            self.db.rollback()

    # ---------------- DELETE ----------------
    def eliminar_producto(self, id_producto):
        query = 'DELETE FROM productos WHERE id = ?'
        try:
            self.db.cursor.execute(query, (id_producto,))
            self.db.commit()
            if self.db.cursor.rowcount > 0:
                print(f'Producto {id_producto} eliminado.')
            else:
                print(f'No se encontró producto con id {id_producto}.')
        except sqlite3.Error as e:
            print(f'Error al eliminar: {e}')
            self.db.rollback()

    def vaciar_tabla(self):
        try:
            self.db.cursor.execute('DELETE FROM productos')
            self.db.cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'productos'")
            self.db.commit()
            print('Tabla vaciada y contador reiniciado.')
        except sqlite3.Error as e:
            print(f'Error al vaciar tabla: {e}')
            self.db.rollback()

    # ---------------- Cierre ----------------
    def cerrar(self):
        self.db.close()
        print(f"Conexión a '{self.db.name}' cerrada.")