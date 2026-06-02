#datos_sinteticos. CARGAR LOS DATOS SINTETICOS EN LA BASE DE DATOS
import psycopg2
from database import get_db_connection

def cargar_datos_sinteticos():
    conection = get_db_connection()
    cur = conection.cursor()
    #verificar si los datos ya estan cargados, si no lo estan, cargarlos
    query = """
    SELECT COUNT(*)
    FROM usuarios
    """
    cur.execute(query)
    count = cur.fetchone()[0]

    if count == 0:
        with open("datos_sinteticos.sql", "r", encoding="utf-8") as f:
            sql = f.read()
            cur.execute(sql)
            print("Datos cargados correctamente")
    else:
        print("Los datos ya están cargados")

    conection.commit()
    cur.close()
    conection.close()

    