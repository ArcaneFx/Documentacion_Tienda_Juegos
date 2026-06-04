import bcrypt
from database import get_db_connection


def register_user(nombre_usuario, correo, password):

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        # HASH DE CONTRASEÑA
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        query = """
        INSERT INTO usuarios
        (nombre_usuario, correo_electronico, contrasena_hash)
        VALUES (%s, %s, %s)
        RETURNING usuario_id
        """

        values = (
            nombre_usuario,
            correo,
            password_hash
        )

        cursor.execute(query, values)
        usuario_id = cursor.fetchone()[0]

        # Crear un método de pago automáticamente para que el usuario
        # pueda comprar juegos apenas se registra
        cursor.execute("""
            INSERT INTO metodos_pago
                (usuario_id, proveedor, ultimos_cuatro_digitos, es_predeterminado)
            VALUES (%s, 'Visa', '0000', TRUE)
        """, (usuario_id,))

        connection.commit()

        print("Usuario registrado correctamente")

    except Exception as e:
        print("Error:", e)

    finally:
        cursor.close()
        connection.close()


def login_user(nombre_usuario, password):

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT usuario_id, contrasena_hash
        FROM usuarios
        WHERE nombre_usuario = %s
        """

        cursor.execute(query, (nombre_usuario,))

        user = cursor.fetchone()

        # usuario no existe
        if user is None:
            print("Usuario no encontrado")
            return None

        usuario_id = user[0]
        password_hash = user[1]

        # verificar contraseña
        password_correcta = bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )

        if password_correcta:

            print("Login exitoso")
            return usuario_id

        else:

            print("Contraseña incorrecta")
            return None

    except Exception as e:
        print("Error:", e)

    finally:
        cursor.close()
        connection.close()
