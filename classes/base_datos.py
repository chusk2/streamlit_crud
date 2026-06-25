import sqlite3
from pathlib import Path

class BaseDatos:
    """
    Gestiona la conexión y operaciones básicas con una base de datos SQLite.
    
    Esta clase proporciona una interfaz simplificada para conectarse a una BD SQLite,
    ejecutar consultas y gestionar transacciones (commit/rollback).
    
    Las filas devueltas por los SELECT son objetos `sqlite3.Row`, lo que
    permite acceder a las columnas por nombre (fila['precio']) además
    de por índice (fila[3]). Esto se configura en `create_connection`.
    
    Attributes:
        db_file (Path): Ruta al archivo de base de datos SQLite.
        name (str): Nombre de la base de datos (sin extensión).
        conn (sqlite3.Connection): Conexión activa a la BD, None si no está conectado.
        cursor (sqlite3.Cursor): Cursor para ejecutar consultas, None si no hay conexión.
    
    Example:
        >>> bd = BaseDatos('inventario')
        >>> bd.create_connection()
        >>> # ... ejecutar consultas con bd.cursor ...
        >>> bd.commit()
        >>> bd.close()
    """

    def __init__(self, db_file):
        """
        Inicializa la clase y prepara el archivo de base de datos.
        
        Crea un directorio 'datos' si no existe y reserva el archivo de BD.
        No establece la conexión automáticamente (ver create_connection).
        
        Args:
            db_name (str): Nombre del archivo de BD sin extensión.
                          Se guardará como 'datos/{db_name}.db'
        """
        # comprueba si existe el archivo y en caso contrario
        # avisa de que se creará. Igualmente, si no existe,
        # sqlite3.connection() lo creará nuevo.
        self.db_file = Path(db_file).resolve()
        self.name = self.db_file.name

        if not self.db_file.exists():
            print(f"El archivo {self.db_file} no existe. Se creará el archivo de base de datos.")
        print(self.db_file)
        # crea la conexión usando el archivo
        self.create_connection()

    def create_connection(self):
        """
        Establece la conexión con la base de datos SQLite.
        
        Crea los atributos self.conn y self.cursor si la conexión es exitosa.
        Los asigna a None en caso de error.
        
        Raises:
            Exception: Captura excepciones de conexión y las imprime.
        """
        try:
            self.conn = sqlite3.connect(self.db_file, check_same_thread=False)

            # ----------------------------------------------------------
            # row_factory: cómo queremos recibir las filas de los SELECT
            # ----------------------------------------------------------
            # Por defecto, sqlite3 devuelve cada fila como una tupla:
            #     (1, 'iPhone 15 Pro', 'Apple', 1199.0, ...)
            # Esto obliga a acordarse del orden de las columnas y a usar
            # índices: fila[1] para el nombre, fila[3] para el precio...
            #
            # Asignando `sqlite3.Row` como row_factory, sqlite3 envuelve
            # cada fila en un objeto que permite acceder a las columnas
            # tanto por índice (fila[1]) como por nombre (fila['nombre']).
            # El código que consuma esta clase queda mucho más legible,
            # y es lo que esperan las plantillas de Jinja2 cuando hacen
            # `{{ producto.nombre }}` en el HTML.
            self.conn.row_factory = sqlite3.Row

            print("Conexión creada con éxito.")
        except Exception as e:
            print(f"Error al crear la base de datos: {e}")
            self.conn, self.cursor = None, None

        else:
            self.cursor = self.conn.cursor()

    def commit(self):
        """
        Confirma (persiste) los cambios en la base de datos.
        
        Raises:
            ConnectionError: Si no hay una conexión activa.
        """
        if self.conn:
            self.conn.commit()
            print("Cambios guardados en la base de datos.")
        else:
            raise ConnectionError("La base de datos no tiene una conexión válida.")
        
    def rollback(self):
        """
        Descarta los cambios pendientes (revierte a la última confirmación).
        
        Raises:
            ConnectionError: Si no hay una conexión activa.
        """
        if self.conn:
            self.conn.rollback()
            print("Los cambios aplicados fueron descartados.")
        else:
            raise ConnectionError("La base de datos no tiene una conexión válida.")
        
    def close(self):
        """
        Cierra la conexión con la base de datos.
        
        Libera los recursos asociados. Debe llamarse al finalizar.
        
        Raises:
            ConnectionError: Si no hay una conexión activa.
        """
        if self.conn:
            self.conn.close()
            print("La conexión se cerró con éxito.")
        else:
            raise ConnectionError("La base de datos no tiene una conexión válida.")