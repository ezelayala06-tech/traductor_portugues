import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name="database/traductor_pt_es.db"):
        self.db_name = db_name
        os.makedirs(os.path.dirname(self.db_name), exist_ok=True)
        self._crear_tablas()
        self._cargar_datos_iniciales()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def _crear_tablas(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Tabla de diccionario local y falsos cognados
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS diccionario (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    portugues TEXT NOT NULL UNIQUE,
                    espanol TEXT NOT NULL,
                    categoria TEXT NOT NULL
                )
            """)
            # Tabla de historial de traducciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historial (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    texto_origen TEXT NOT NULL,
                    texto_traducido TEXT NOT NULL,
                    fecha DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def _cargar_datos_iniciales(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM diccionario")
            if cursor.fetchone()[0] == 0:
                # Falsos Cognados / Falsos Amigos y palabras de uso universitario
                palabras = [
                    ("escritório", "oficina", "falso_amigo"),
                    ("propina", "soborno", "falso_amigo"),
                    ("embarazada", "avergonzada", "falso_amigo"),
                    ("pasta", "carpeta / pasta", "falso_amigo"),
                    ("sobrenome", "apellido", "falso_amigo"),
                    ("borracha", "goma de borrar", "falso_amigo"),
                    ("esquisito", "raro / extraño", "falso_amigo"),
                    ("aula", "clase", "universidad"),
                    ("aluno", "estudiante", "universidad"),
                    ("prova", "examen", "universidad"),
                    ("obrigado", "gracias", "saludo")
                ]
                cursor.executemany(
                    "INSERT OR IGNORE INTO diccionario (portugues, espanol, categoria) VALUES (?, ?, ?)",
                    palabras
                )
                conn.commit()

    def registrar_traduccion(self, origen, traducido):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO historial (texto_origen, texto_traducido) VALUES (?, ?)",
                (origen, traducido)
            )
            conn.commit()

    def buscar_falso_amigo(self, palabra):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT espanol, categoria FROM diccionario WHERE LOWER(portugues) = LOWER(?)",
                (palabra.strip(),)
            )
            return cursor.fetchone()

    def agregar_palabra(self, pt, es, cat):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO diccionario (portugues, espanol, categoria) VALUES (?, ?, ?)",
                (pt.strip().lower(), es.strip(), cat)
            )
            conn.commit()

    def obtener_historial(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT texto_origen, texto_traducido, fecha FROM historial ORDER BY id DESC LIMIT 20")
            return cursor.fetchall()