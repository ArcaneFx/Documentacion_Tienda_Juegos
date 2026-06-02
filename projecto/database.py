#SOLO CONEXION A BASE DE DATOS
import psycopg2

def get_db_connection():
    try:
        #todos los datos de la conexion a la base de datos
        #los mismos que se usan en dbeaver
        
        connection = psycopg2.connect( 
            host="localhost",
            database="steam", #nombre de la base de datos (yo le tengo llamada asi)
            user="postgres", 
            password="1234", #respectivo password de cada uno
            port=5432
        )
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None