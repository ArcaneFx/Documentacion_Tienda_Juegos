import os  # <-- Librería nativa para manejar rutas en cualquier PC (por si acaso)
from database import get_db_connection


def ejecutar_archivo_sql(cursor, nombre_archivo):
    """Busca el archivo SQL en la misma carpeta de este script y lo ejecuta."""
    # 1. Encuentra la carpeta exacta donde está guardado datos_sinteticos.py (proyectof)
    carpeta_del_script = os.path.dirname(os.path.abspath(__file__))

    # 2. Construye la ruta hacia el archivo .sql que está a su lado
    ruta_absoluta = os.path.join(carpeta_del_script, nombre_archivo)

    # 3. Abre y lee el archivo limpiamente
    with open(ruta_absoluta, "r", encoding="utf-8") as archivo:
        sql = archivo.read()
    cursor.execute(sql)


def cargar_datos_sinteticos():
    conexion = get_db_connection()
    cur = conexion.cursor()

    try:
        # Contar usuarios existentes
        cur.execute("SELECT COUNT(*) FROM usuarios")
        cantidad_usuarios = cur.fetchone()[0]

        print(f"Usuarios encontrados: {cantidad_usuarios}")

        # CASO 1: Base vacía → cargar los 40.000 datos sintéticos
        if cantidad_usuarios == 0:
            print("Base vacía.")
            print("Cargando datos_sinteticos.sql ...")
            # Le pasamos solo el nombre del archivo, la función se encarga del resto
            ejecutar_archivo_sql(cur, "datos_sinteticos.sql")
            conexion.commit()
            print("Datos sintéticos principales cargados correctamente.")

        # CASO 2: Ya están los 500 sintéticos → cargar los usuarios de demostración
        elif cantidad_usuarios == 500:
            print("Se detectaron 500 usuarios.")
            print("Cargando usuarios de demostración...")
            ejecutar_archivo_sql(cur, "datos_sinteticos_de_prueba.sql")
            conexion.commit()
            print("Usuarios de demostración cargados correctamente.")

        # CASO 3: Ya están ambos archivos cargados
        elif cantidad_usuarios >= 503:
            print(
                "La base ya contiene los datos sintéticos y los usuarios de demostración."
            )

        # CASO 4: Estado inesperado
        else:
            print(
                f"Cantidad de usuarios inesperada ({cantidad_usuarios}).\n"
                "No se cargó ningún archivo para evitar duplicados."
            )

    except Exception as e:
        conexion.rollback()
        print(f"Error al cargar datos: {e}")

    finally:
        cur.close()
        conexion.close()


if __name__ == "__main__":
    cargar_datos_sinteticos()