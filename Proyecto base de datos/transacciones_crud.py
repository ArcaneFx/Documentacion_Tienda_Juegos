# transacciones_crud.py
# Integrante: Parra
# Funciones que ingresan y eliminan datos de la base de datos.

import bcrypt
from datetime import datetime
from database import get_db_connection


def agregar_al_carrito(usuario_id, juego_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Consulta SQL de inserción para agregar un juego al carrito del usuario
        # Trabaja con usuario_id y juego_id para relacionar el carrito con el usuario y el juego específico
        sql = """
                INSERT INTO carrito_compras (usuario_id, juego_id)
                VALUES (%s, %s)
                RETURNING carrito_item_id;
            """

        # Se ocupa (%s, %s) en vez de los valores directamente para evitar SQL injection
        cur.execute(sql, (usuario_id, juego_id))
        carrito_item_id = cur.fetchone()[0]  # Obtiene el ID del nuevo item en el carrito
        conn.commit()  # Confirma la transacción para guardar los cambios en la base de datos

        cur.close()  # Cierra el cursor después de la operación
        conn.close()  # Cierra la conexión a la base de datos

        return True, f"Juego añadido al carrito correctamente (ID Ítem: {carrito_item_id})"

    except Exception as error:
        # Manejo de errores para detectar si el juego ya está en el carrito
        error_msg = str(error).lower()
        if "duplicate" in error_msg or "ya existe" in error_msg:
            return False, "Este juego ya está en tu carrito de compras."

        # Si ocurre cualquier otro error, se devuelve un mensaje genérico de error inesperado
        return False, f"Error inesperado en la base de datos: {error}"


def procesar_compra_juego(usuario_id, juego_id, precio_juego, usar_cartera=True):
    """Procesa la compra de un juego, aplicando el saldo de la cartera del usuario si se desea."""

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Verificar el saldo de la cartera del usuario (está en la tabla usuarios)
        cur.execute("SELECT saldo_cartera FROM usuarios WHERE usuario_id = %s", (usuario_id,))
        saldo_cartera = cur.fetchone()[0]

        monto_a_descontar_cartera = 0.0
        monto_pago_externo = precio_juego

        # Determinar cuánto se descontará de la cartera y cuánto se pagará externamente
        if usar_cartera and saldo_cartera > 0:
            if saldo_cartera >= precio_juego:
                # Caso 1: El saldo de la cartera es suficiente para cubrir el precio del juego
                monto_a_descontar_cartera = precio_juego
                monto_pago_externo = 0.0
            else:
                # Caso 2: el saldo no es suficiente, se usa todo y el resto se paga externamente
                monto_a_descontar_cartera = float(saldo_cartera)
                monto_pago_externo = float(precio_juego) - monto_a_descontar_cartera

        # Descontar el saldo de la cartera si corresponde
        if monto_a_descontar_cartera > 0:
            sql_actualizar_saldo = """
                UPDATE usuarios 
                SET saldo_cartera = saldo_cartera - %s 
                WHERE usuario_id = %s;
            """
            cur.execute(sql_actualizar_saldo, (monto_a_descontar_cartera, usuario_id))

        # Registrar la transacción (metodo_pago_id viene del usuario)
        cur.execute("SELECT metodo_pago_id FROM metodos_pago WHERE usuario_id = %s LIMIT 1", (usuario_id,))
        metodo_pago_id = cur.fetchone()[0]

        sql_boleta = """
            INSERT INTO transacciones (usuario_id, metodo_pago_id, monto_total, estado)
            VALUES (%s, %s, %s, 'completado')
            RETURNING transaccion_id;
        """
        cur.execute(sql_boleta, (usuario_id, metodo_pago_id, precio_juego))
        transaccion_id = cur.fetchone()[0]

        # Registrar en biblioteca para que el usuario tenga acceso al juego comprado
        sql_biblioteca = """
            INSERT INTO biblioteca (usuario_id, juego_id, fecha_compra)
            VALUES (%s, %s, %s);
        """
        cur.execute(sql_biblioteca, (usuario_id, juego_id, datetime.now()))

        # Limpiar el carrito del usuario después de procesar la compra
        sql_limpiar_carrito = """
            DELETE FROM carrito_compras 
            WHERE usuario_id = %s AND juego_id = %s;
        """
        cur.execute(sql_limpiar_carrito, (usuario_id, juego_id))

        # Si las 4 operaciones anteriores salieron bien, se confirma la transacción
        conn.commit()

        cur.close()
        conn.close()

        # Mensaje para la interfaz
        resumen = f"¡Compra exitosa! Boleta N° {transaccion_id}.\n"
        resumen += f"Descontado de la cartera: ${monto_a_descontar_cartera:.2f}\n"
        resumen += f"Pagado con tarjeta (simulado): ${monto_pago_externo:.2f}\n"
        resumen += "El juego ya está en tu biblioteca."

        return True, resumen  # ← faltaba este return

    except Exception as error:
        # Si ocurre un error, se revierten TODOS los cambios
        if conn:
            conn.rollback()  # ← faltaban los paréntesis
            conn.close()

        return False, f"La transacción falló y fue cancelada de forma segura: {error}"


def registrar_usuario(nombre_usuario, correo_electronico, contrasena_hash):
    """Permite registrar un nuevo jugador en el sistema.
    Controla que no se repitan correos o nombres de usuario únicos."""

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Consulta SQL de inserción para registrar un nuevo usuario
        sql = """
            INSERT INTO usuarios (nombre_usuario, correo_electronico, contrasena_hash)
            VALUES (%s, %s, %s)
            RETURNING usuario_id;
        """

        cur.execute(sql, (nombre_usuario, correo_electronico, contrasena_hash))
        usuario_id = cur.fetchone()[0]

        # Crear método de pago automáticamente para que pueda comprar juegos
        cur.execute("""
            INSERT INTO metodos_pago
                (usuario_id, proveedor, ultimos_cuatro_digitos, es_predeterminado)
            VALUES (%s, 'Visa', '0000', TRUE)
        """, (usuario_id,))

        conn.commit()
        cur.close()
        conn.close()

        return True, f"¡Usuario registrado con éxito! Tu ID es: {usuario_id}"

    except Exception as error:
        # Manejo de errores para detectar si el nombre de usuario o correo ya están registrados
        error_msg = str(error).lower()
        if "duplicate" in error_msg or "ya existe" in error_msg:
            return False, "El nombre de usuario o el correo electrónico ya están registrados."
        return False, f"Error al registrar usuario: {error}"


def cargar_saldo_cartera(usuario_id, monto_a_cargar):
    """Permite al usuario abonar dinero a su saldo de la billetera virtual."""

    if monto_a_cargar <= 0:
        return False, "El monto a cargar debe ser mayor a $0."

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Sumar el monto al saldo actual del usuario
        sql = """
            UPDATE usuarios 
            SET saldo_cartera = saldo_cartera + %s 
            WHERE usuario_id = %s;
        """
        cur.execute(sql, (monto_a_cargar, usuario_id))

        conn.commit()
        cur.close()
        conn.close()

        return True, f"Se han cargado ${monto_a_cargar:.2f} a tu billetera exitosamente."

    except Exception as error:
        return False, f"Error al cargar saldo a la cartera: {error}"


def eliminar_juego_carrito(usuario_id, juego_id):
    """Elimina un juego específico del carrito de compras del usuario."""

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM carrito_compras
            WHERE usuario_id = %s AND juego_id = %s
            RETURNING carrito_item_id;
        """, (usuario_id, juego_id))

        eliminado = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if eliminado:
            return True, "Juego eliminado del carrito correctamente."
        else:
            return False, "El juego no estaba en el carrito."

    except Exception as error:
        return False, f"Error al eliminar del carrito: {error}"


def eliminar_usuario(usuario_id):
    """Elimina un usuario del sistema (y en cascada todo lo asociado)."""

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM usuarios
            WHERE usuario_id = %s
            RETURNING usuario_id;
        """, (usuario_id,))

        eliminado = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if eliminado:
            return True, f"Usuario {usuario_id} eliminado correctamente."
        else:
            return False, "No se encontró el usuario."

    except Exception as error:
        return False, f"Error al eliminar usuario: {error}"


def publicar_resena(usuario_id, juego_id, contenido, recomendado=True):
    """Permite al usuario escribir una reseña sobre un juego que posee."""

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Verificar que el usuario posee el juego en su biblioteca
        cur.execute("SELECT 1 FROM biblioteca WHERE usuario_id = %s AND juego_id = %s;",
                    (usuario_id, juego_id))
        posee_juego = cur.fetchone()

        if not posee_juego:
            cur.close()
            conn.close()
            return False, "No puedes reseñar un juego que no tienes en tu biblioteca."

        sql = """
            INSERT INTO resenas (usuario_id, juego_id, contenido, recomendado)
            VALUES (%s, %s, %s, %s)
            RETURNING resena_id;
        """
        cur.execute(sql, (usuario_id, juego_id, contenido, recomendado))
        resena_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        return True, f"Reseña publicada con éxito (ID: {resena_id})."

    except Exception as error:
        return False, f"Error al publicar la reseña: {error}"