from database import get_db_connection


# ══════════════════════════════════════════════
#  JUEGOS
# ══════════════════════════════════════════════

def contar_juegos():
    """Retorna el total de juegos en la base de datos."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM juegos")
        total = cursor.fetchone()[0]
        return total
    except Exception as e:
        print("Error:", e)
        return 0
    finally:
        cursor.close()
        connection.close()


def listar_juegos(limite=10, offset=0):
    """Lista todos los juegos disponibles en la tienda con su categoría y precio."""

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT j.juego_id,
               j.titulo,
               c.nombre    AS categoria,
               j.precio,
               j.desarrollador
        FROM juegos j
        JOIN juegos_categorias jc ON j.juego_id     = jc.juego_id
        JOIN categorias c         ON jc.categoria_id = c.categoria_id
        ORDER BY j.titulo ASC
        LIMIT %s OFFSET %s
        """

        cursor.execute(query, (limite, offset))
        juegos = cursor.fetchall()

        return juegos

    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        connection.close()


def buscar_juego_por_nombre(titulo_busqueda):
    """Busqueda parcial de juegos por titulo."""

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT j.juego_id,
               j.titulo,
               c.nombre    AS categoria,
               j.precio,
               j.descripcion
        FROM juegos j
        JOIN juegos_categorias jc ON j.juego_id     = jc.juego_id
        JOIN categorias c         ON jc.categoria_id = c.categoria_id
        WHERE LOWER(j.titulo) LIKE LOWER(%s)
        ORDER BY j.titulo ASC
        """

        cursor.execute(query, (f"%{titulo_busqueda}%",))
        resultados = cursor.fetchall()

        print(f"\nResultados para '{titulo_busqueda}':")
        print(f"{'─'*55}")
        for juego_id, titulo, categoria, precio, descripcion in resultados:
            print(f"[{juego_id}] {titulo} ({categoria}) - ${precio:.2f}")
            if descripcion:
                print(f"      {descripcion[:80]}")
        if not resultados:
            print("No se encontraron juegos.")
        print(f"{'─'*55}\n")

        return resultados

    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        connection.close()


# ══════════════════════════════════════════════
#  USUARIOS
# ══════════════════════════════════════════════

def mostrar_perfil_usuario(usuario_id):
    """
    Perfil completo de un usuario:
    datos personales + total de juegos en biblioteca y logros desbloqueados.
    """

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT u.usuario_id,
               u.nombre_usuario,
               u.correo_electronico,
               u.saldo_cartera,
               u.fecha_registro,
               COUNT(DISTINCT b.juego_id)   AS total_juegos,
               COUNT(DISTINCT lu.logro_id)  AS total_logros
        FROM usuarios u
        LEFT JOIN biblioteca      b  ON u.usuario_id = b.usuario_id
        LEFT JOIN logros_usuarios lu ON u.usuario_id = lu.usuario_id
        WHERE u.usuario_id = %s
        GROUP BY u.usuario_id
        """

        cursor.execute(query, (usuario_id,))
        perfil = cursor.fetchone()

        if perfil is None:
            print("Usuario no encontrado.")
            return None

        uid, nombre, correo, saldo, fecha_reg, total_juegos, total_logros = perfil

        print(f"\n{'═'*45}")
        print(f"  PERFIL DE USUARIO")
        print(f"{'═'*45}")
        print(f"  ID            : {uid}")
        print(f"  Usuario       : {nombre}")
        print(f"  Correo        : {correo}")
        print(f"  Saldo cartera : ${saldo:.2f}")
        print(f"  Registro      : {fecha_reg.strftime('%d/%m/%Y')}")
        print(f"  Juegos        : {total_juegos}")
        print(f"  Logros        : {total_logros}")
        print(f"{'═'*45}\n")

        return perfil

    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        connection.close()


def mostrar_biblioteca(usuario_id):
    """
    Juegos en la biblioteca de un usuario,
    ordenados por tiempo jugado (mas jugado primero).
    """

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT j.juego_id,
               j.titulo,
               c.nombre               AS categoria,
               b.fecha_compra,
               b.tiempo_jugado_minutos,
               b.ultima_vez_jugado
        FROM biblioteca b
        JOIN juegos j             ON b.juego_id     = j.juego_id
        JOIN juegos_categorias jc ON j.juego_id     = jc.juego_id
        JOIN categorias c         ON jc.categoria_id = c.categoria_id
        WHERE b.usuario_id = %s
        ORDER BY b.tiempo_jugado_minutos DESC
        """

        cursor.execute(query, (usuario_id,))
        biblioteca = cursor.fetchall()

        if not biblioteca:
            print("Este usuario no tiene juegos en su biblioteca.")
            return []

        print(f"\nBiblioteca del usuario {usuario_id}:")
        print(f"{'─'*65}")
        print(f"{'Título':<25} {'Categoría':<13} {'Jugado':>9}  Fecha de compra")
        print(f"{'─'*65}")
        for jid, titulo, categoria, fecha_compra, minutos, ultima in biblioteca:
            horas = minutos // 60
            print(f"{titulo:<25} {categoria:<13} {horas:>7}h  {fecha_compra.strftime('%d/%m/%Y')}")
        print(f"{'─'*65}")
        print(f"Total: {len(biblioteca)} juegos\n")

        return biblioteca

    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        connection.close()


# ══════════════════════════════════════════════
#  LOGROS
# ══════════════════════════════════════════════

def mostrar_carrito(usuario_id):
    """Juegos en el carrito de compras de un usuario con total acumulado."""

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT j.juego_id,
               j.titulo,
               j.precio,
               cc.fecha_agregado
        FROM carrito_compras cc
        JOIN juegos j ON cc.juego_id = j.juego_id
        WHERE cc.usuario_id = %s
        ORDER BY cc.fecha_agregado DESC
        """

        cursor.execute(query, (usuario_id,))
        carrito = cursor.fetchall()

        if not carrito:
            print("El carrito esta vacio.")
            return []

        total = 0
        print(f"\nCarrito del usuario {usuario_id}:")
        print(f"{'─'*50}")
        for juego_id, titulo, precio, fecha in carrito:
            print(f"  [{juego_id}] {titulo:<30} ${precio:.2f}")
            total += precio
        print(f"{'─'*50}")
        print(f"  TOTAL: ${total:.2f}\n")

        return carrito

    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        connection.close()


def mostrar_historial_compras(usuario_id):
    """
    Historial de transacciones de un usuario
    con metodo de pago y monto de cada compra.
    """

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT t.transaccion_id,
               t.monto_total,
               t.estado,
               t.fecha_transaccion,
               mp.proveedor
        FROM transacciones t
        JOIN metodos_pago mp ON t.metodo_pago_id = mp.metodo_pago_id
        WHERE t.usuario_id = %s
        ORDER BY t.fecha_transaccion DESC
        """

        cursor.execute(query, (usuario_id,))
        historial = cursor.fetchall()

        if not historial:
            print("Este usuario no tiene compras registradas.")
            return []

        total_gastado = 0
        print(f"\nHistorial de compras del usuario {usuario_id}:")
        print(f"{'─'*65}")
        print(f"{'#Boleta':<10} {'Monto':>8}  {'Estado':<12} {'Metodo':<15} Fecha")
        print(f"{'─'*65}")
        for t_id, monto, estado, fecha, proveedor in historial:
            print(f"{t_id:<10} ${monto:>7.2f}  {estado:<12} {proveedor:<15} {fecha.strftime('%d/%m/%Y')}")
            total_gastado += monto
        print(f"{'─'*65}")
        print(f"Total gastado: ${total_gastado:.2f}  ({len(historial)} transacciones)\n")

        return historial

    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        connection.close()
