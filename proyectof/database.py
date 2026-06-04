#SOLO CONEXION A BASE DE DATOS
import psycopg2

def get_db_connection():
    try:
        #todos los datos de la conexion a la base de datos
        #los mismos que se usan en dbeaver
        
        connection = psycopg2.connect( 
            host="localhost",
            database="Steam_casi", #nombre de la base de datos (yo le tengo llamada asi)
            user="postgres", 
            password="postgres" #respectivo password de cada uno
        )
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None