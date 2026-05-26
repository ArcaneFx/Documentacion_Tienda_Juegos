import conexion #Conexión a la base de datos (Ruby dale tu corte)
from datetime import datetime


def agregar_al_carrito(usuario_id, juego_id):
    try:
        #Se abre la conexion a la base de datos
        conn = conexion.obtener_conexion()
        cur = conn.cursor()

        #Consulta SQL de inserción para agregar un juego al carrito del usuario
        #Trabaja con usuario_id y juego_id para relacionar el carrito con el usuario y el juego específico
        sql = """
                INSERT INTO carrito_compras (usuario_id, juego_id)
                VALUES (%s, %s)
                RETURNING carrito_item_id;
            """

        #Preguntar al profesor por que se ocupa (%s, %s) en vez de directamente los valores

        cur.execute(sql, (usuario_id, juego_id)) #Ejecuta la consulta SQL con los parámetros proporcionados (usuario_id y juego_id)
        carrito_item_id = cur.fetchone()[0] #Obtiene el ID del nuevo item en el carrito
        conn.commit() #Confirma la transacción para guardar los cambios en la base de datos

        cur.close() #Cierra el cursor después de la operación
        conn.close() #Cierra la conexión a la base de datos

        return True, f"Juego añadido al carrito correctamente (ID Ítem: {carrito_item_id})"
    except Exception as error:
        #Manejo de errores para detectar si el juego ya está en el carrito
        error_msg = str(error).lower()
        if "duplicate" in error_msg or "ya existe" in error_msg:
            return False, "Este juego ya está en tu carrito de compras."
        
        #Si ocurre cualquier otro error, se devuelve un mensaje genérico de error inesperado
        return False, f"Error inesperado en la base de datos: {error}"
    
def procesar_compra_juego(usuario_id, juego_id, precio_juego, usar_cartera=True):
    """Procesa la compra de un juego, aplicando el saldo de la cartera del usuario si se desea"""
    
    
    
    conn = None
    try:
        #abrir la conexión a la base de datos
        conn = conexion.conectar()
        cur= conn.cursor()

        #
        #Verificar el saldo de la cartera del usuario 
        cur.execute("SELECT saldo FROM cartera WHERE usuario_id = %s", (usuario_id,))
        saldo_cartera = cur.fetchone()[0]

        monto_a_descontar_cartera = 0.0
        monto_pago_externo = precio_juego

        #Determinar cuánto se descontará de la cartera y cuánto se pagará externamente
        if usar_cartera and saldo_cartera > 0:
            if saldo_cartera >= precio_juego:
                #Caso 1: El saldo de la cartera es suficiente para cubrir el precio del juego
                monto_a_descontar_cartera = precio_juego
                monto_pago_externo = 0.0
            else:
                #Caso 2: el saldo de la cartera no es suficiente, se usa todo el saldo disponible y el resto se paga externamente
                monto_a_descontar_cartera = float(saldo_cartera)
                monto_pago_externo = float(precio_juego) - monto_a_descontar_cartera


        #Registrar la compra en la tabla de compras, incluyendo el monto pagado con la cartera y el monto pagado externamente
        if monto_a_descontar_cartera > 0:
            sql_actualizar_saldo = """
                UPDATE usuarios 
                SET saldo_cartera = saldo_cartera - %s 
                WHERE usuario_id = %s;
            """
            cur.execute(sql_actualizar_saldo, (monto_a_descontar_cartera, usuario_id))

        #Registrar la transacción en la tabla de transacciones, indicando el método de pago utilizado (cartera, tarjeta, etc.) y el monto total de la compra
        # Usamos el 'metodo_pago_id' = 1 para simplificar temporalmente 
        sql_boleta = """
            INSERT INTO transacciones (usuario_id, metodo_pago_id, monto_total, estado)
            VALUES (%s, 1, %s, 'completado')
            RETURNING transaccion_id;
        """
        cur.execute(sql_boleta, (usuario_id, precio_juego))
        transaccion_id = cur.fetchone()[0]

        #Registrar la compra en la tabla de biblioteca para que el usuario tenga acceso al juego comprado
        sql_biblioteca = """
            INSERT INTO biblioteca (usuario_id, juego_id, fecha_compra)
            VALUES (%s, %s, %s);
        """
        cur.execute(sql_biblioteca, (usuario_id, juego_id, datetime.now()))

        #Limpiar el carrito del usuario después de procesar la compra, eliminando el juego comprado del carrito
        sql_limpiar_carrito = """
            DELETE FROM carrito_compras 
            WHERE usuario_id = %s AND juego_id = %s;
        """
        cur.execute(sql_limpiar_carrito, (usuario_id, juego_id))

        #Si PostGreSQL ejecuto las 4 ordenes anteriores sin errores, se confirma la transacción para guardar los cambios en la base de datos

        conn.commit()

        cur.close() #Cierra el cursor después de la operación
        conn.close() #Cierra la conexión a la base de datos

        #Mensaje para la interfaz
        resumen = f"¡Compra exitosa! Boleta N° {transaccion_id}.\n"
        resumen += f"Descontado de la cartera: ${monto_a_descontar_cartera:.2f}\n"
        resumen += f"Pagado con tarjeta (simulado): ${monto_pago_externo:.2f}\n"
        resumen += "El juego ya está en tu biblioteca."

    except Exception as error:
        #Si en cualquiera de las 4 ordenes ocurre un error ninguna de las ordenes se ejecutará 
        #y se revertirán los cambios realizados en la base de datos
        if conn:
            conn.rollback
            conn.close()

        return False, f"La transacción falló y fue cancelada de forma segura: {error}"

def registrar_usuario(nombre_usuario, correo_electronico, contrasena_hash):
    """Permite registrar un nuevo jugador en el sistema.
    Controla que no se repitan correos o nombres de usuario únicos."""

    try:
        # Abrir la conexión a la base de datos
        conn = conexion.obtener_conexion()
        cur = conn.cursor()


        #Consulta SQL de inserción para registrar un nuevo usuario, asegurando que el nombre de usuario
        #y el correo electrónico sean únicos en la base de datos
        sql = """
            INSERT INTO usuarios (nombre_usuario, correo_electronico, contrasena_hash)
            VALUES (%s, %s, %s)
            RETURNING usuario_id;
        """

        #Ejecutar la consulta SQL con los parámetros proporcionados (nombre_usuario, correo_electronico, contrasena_hash)
        cur.execute(sql, (nombre_usuario, correo_electronico, contrasena_hash))
        usuario_id = cur.fetchone()[0]



        conn.commit()  #Confirmar la transacción para guardar los cambios en la base de datos
        cur.close() #Cerrar el cursor después de la operación
        conn.close() #Cerrar la conexión a la base de datos
        return True, f"¡Usuario registrado con éxito! Tu ID es: {usuario_id}"  #Mensaje para la interfaz

    except Exception as error:
        #Manejo de errores para detectar si el nombre de usuario o el correo electrónico ya están registrados
        error_msg = str(error).lower() 
        if "duplicate" in error_msg or "ya existe" in error_msg:
            return False, "El nombre de usuario o el correo electrónico ya están registrados."
        return False, f"Error al registrar usuario: {error}"
    
def cargar_saldo_cartera(usuario_id, monto_a_cargar):
    """
    Permite al usuario abonar dinero a su saldo de la billetera virtual.
    """

    if monto_a_cargar <= 0:
        return False, "El monto a cargar debe ser mayor a $0."
    
    try:
        #Abrir la conexión a la base de datos
        conn = conexion.conectar() 
        cur = conn.cursor() 
        

        #Consulta SQL para actualizar el saldo de la cartera del usuario, 
        #sumando el monto a cargar al saldo actual
        sql = """
            UPDATE usuarios 
            SET saldo_cartera = saldo_cartera + %s 
            WHERE usuario_id = %s;
        """
        #Ejecutar la consulta SQL con los parámetros proporcionados (monto_a_cargar y usuario_id)
        cur.execute(sql, (monto_a_cargar, usuario_id)) 

        conn.commit() #Confirmar la transacción para guardar los cambios en la base de datos
        cur.close() #Cerrar el cursor después de la operación
        conn.close() #Cerrar la conexión a la base de datos
        return True, f"Se han cargado ${monto_a_cargar:.2f} a tu billetera exitosamente." #Mensaje para la interfaz

    except Exception as error:
        return False, f"Error al cargar saldo a la cartera: {error}"


#Esta funcion por ahora no la utilizaremos o tal vez si pero la hago por si acaso
def publicar_resena(usuario_id, juego_id, contenido, recomendado=True):
    """
    Permite al usuario escribir una reseña sobre un juego que posee.
    """
    try:
        conn = conexion.conectar() 
        cur = conn.cursor()
        
        #Verificar que el usuario posee el juego en su biblioteca antes de permitir publicar una reseña
        cur.execute("SELECT 1 FROM biblioteca WHERE usuario_id = %s AND juego_id = %s;", (usuario_id, juego_id))
        posee_juego = cur.fetchone()
        
        if not posee_juego:
            cur.close()
            conn.close()
            return False, "No puedes reseñar un juego que no tienes en tu biblioteca."
            
        #Insertar la reseña en la tabla de reseñas, relacionándola con el usuario y el juego correspondiente    
        sql = """
            INSERT INTO resenas (usuario_id, juego_id, contenido, recomendado)
            VALUES (%s, %s, %s, %s)
            RETURNING resena_id;
        """

        #Ejecutar la consulta SQL con los parámetros proporcionados (usuario_id, juego_id, contenido, recomendado)
        cur.execute(sql, (usuario_id, juego_id, contenido, recomendado))
        resena_id = cur.fetchone()[0] #Obtener el ID de la nueva reseña creada para incluirlo en el mensaje de éxito
        
        conn.commit()
        cur.close()
        conn.close()
        return True, f"Reseña publicada con éxito (ID: {resena_id})." #Mensaje de éxito para la interfaz, incluyendo el ID de la reseña publicada
        
    except Exception as error:
        return False, f"Error al publicar la reseña: {error}" #Mensaje de error para la interfaz


