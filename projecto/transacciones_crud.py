from datetime import datetime
# Importamos la conexión real desde la carpeta hermana o el mismo directorio
from database import get_db_connection

def agregar_al_carrito(usuario_id, juego_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        sql = """
            INSERT INTO carrito_compras (usuario_id, juego_id)
            VALUES (%s, %s)
            RETURNING carrito_item_id;
        """

        cur.execute(sql, (usuario_id, juego_id)) 
        carrito_item_id = cur.fetchone()[0] 
        conn.commit() 

        cur.close() 
        conn.close() 

        return True, f"Juego añadido al carrito correctamente (ID Ítem: {carrito_item_id})"
    except Exception as error:
        error_msg = str(error).lower()
        if "duplicate" in error_msg or "ya existe" in error_msg:
            return False, "Este juego ya está en tu carrito de compras."
        return False, f"Error inesperado en la base de datos: {error}"
    
def procesar_compra_juego(usuario_id, juego_id, precio_juego, usar_cartera=True):
    """Procesas la compra de un juego en una sola transacción atómica"""
    conn = get_db_connection()
    if not conn:
        return False, "No se pudo establecer conexión con la base de datos."
        
    cur = conn.cursor()
    try:
        # Corregido: El saldo está en la tabla usuarios como saldo_cartera
        cur.execute("SELECT saldo_cartera FROM usuarios WHERE usuario_id = %s", (usuario_id,))
        saldo_cartera = float(cur.fetchone()[0])

        monto_a_descontar_cartera = 0.0
        monto_pago_externo = float(precio_juego)

        if usar_cartera and saldo_cartera > 0:
            if saldo_cartera >= precio_juego:
                monto_a_descontar_cartera = float(precio_juego)
                monto_pago_externo = 0.0
            else:
                monto_a_descontar_cartera = saldo_cartera
                monto_pago_externo = float(precio_juego) - monto_a_descontar_cartera

        # 1. Descontar de la billetera virtual si corresponde
        if monto_a_descontar_cartera > 0:
            sql_actualizar_saldo = """
                UPDATE usuarios 
                SET saldo_cartera = saldo_cartera - %s 
                WHERE usuario_id = %s;
            """
            cur.execute(sql_actualizar_saldo, (monto_a_descontar_cartera, usuario_id))

        # 2. Registrar la boleta transaccional (Suponiendo método_pago_id = 1 para pruebas)
        sql_boleta = """
            INSERT INTO transacciones (usuario_id, metodo_pago_id, monto_total)
            VALUES (%s, 1, %s)
            RETURNING transaccion_id;
        """
        cur.execute(sql_boleta, (usuario_id, precio_juego))
        transaccion_id = cur.fetchone()[0]

        # 3. Registrar el activo digital en la biblioteca del jugador
        sql_biblioteca = """
            INSERT INTO biblioteca (usuario_id, juego_id, fecha_compra)
            VALUES (%s, %s, %s);
        """
        cur.execute(sql_biblioteca, (usuario_id, juego_id, datetime.now()))

        # 4. Limpiar el carrito de compras
        sql_limpiar_carrito = """
            DELETE FROM carrito_compras 
            WHERE usuario_id = %s AND juego_id = %s;
        """
        cur.execute(sql_limpiar_carrito, (usuario_id, juego_id))

        # CONFIRMACIÓN DE LA TRANSACCIÓN (Propiedad ACID)
        conn.commit()

        cur.close() 
        conn.close() 

        resumen = f"¡Compra exitosa! Boleta N° {transaccion_id}.\n"
        resumen += f"Descontado de la cartera: ${monto_a_descontar_cartera:.2f}\n"
        resumen += f"Pagado con tarjeta (simulado): ${monto_pago_externo:.2f}\n"
        resumen += "El juego ya está disponible en tu biblioteca."
        return True, resumen

    except Exception as error:
        # Corregido: Se agregaron los paréntesis al rollback()
        if conn:
            conn.rollback()
            conn.close()
        return False, f"La transacción falló y fue cancelada de forma segura: {error}"

def cargar_saldo_cartera(usuario_id, monto_a_cargar):
    if monto_a_cargar <= 0:
        return False, "El monto a cargar debe ser mayor a $0."
    
    try:
        conn = get_db_connection() 
        cur = conn.cursor() 
        
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

def publicar_resena(usuario_id, juego_id, contenido, recomendado=True):
    try:
        conn = get_db_connection() 
        cur = conn.cursor()
        
        cur.execute("SELECT 1 FROM biblioteca WHERE usuario_id = %s AND juego_id = %s;", (usuario_id, juego_id))
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