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


def listar_juegos_por_categoria(categoria, orden="ventas"):
    """
    Lista juegos de una categoría específica.
    Parámetro orden: 'ventas', 'precio_asc', 'precio_desc', 'aprobacion'
    """
    ORDENES = {
        "ventas":      "copias_vendidas DESC",
        "precio_asc":  "j.precio ASC",
        "precio_desc": "j.precio DESC",
        "aprobacion":  "aprobacion_pct DESC NULLS LAST",
    }
    orden_sql = ORDENES.get(orden, "copias_vendidas DESC")

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = f"""
        SELECT j.juego_id,
               j.titulo,
               j.precio,
               j.desarrollador,
               COUNT(DISTINCT b.usuario_id)                             AS copias_vendidas,
               ROUND(
                   AVG(CASE WHEN r.recomendado THEN 1.0 ELSE 0.0 END) * 100, 1
               )                                                        AS aprobacion_pct
        FROM juegos j
        JOIN juegos_categorias jc ON j.juego_id     = jc.juego_id
        JOIN categorias c         ON jc.categoria_id = c.categoria_id
        LEFT JOIN biblioteca b    ON j.juego_id     = b.juego_id
        LEFT JOIN resenas r       ON j.juego_id     = r.juego_id
        WHERE LOWER(c.nombre) = LOWER(%s)
        GROUP BY j.juego_id, j.titulo, j.precio, j.desarrollador
        ORDER BY {orden_sql}
        """

        cursor.execute(query, (categoria,))
        juegos = cursor.fetchall()

        print(f"\nCategoria: {categoria.upper()}  (orden: {orden})")
        print(f"{'─'*70}")
        print(f"{'Título':<28} {'Precio':>7}  {'Ventas':>7}  {'Aprob.':>7}  Desarrollador")
        print(f"{'─'*70}")
        for jid, titulo, precio, dev, ventas, aprob in juegos:
            aprob_str = f"{aprob:.1f}%" if aprob is not None else "  N/A"
            print(f"{titulo:<28} ${precio:>6.2f}  {ventas:>7,}  {aprob_str:>7}  {dev or 'N/A'}")
        print(f"{'─'*70}")
        print(f"Total: {len(juegos)} juegos en '{categoria}'\n")

        return juegos

    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        connection.close()


def listar_juegos_por_precio(precio_min=0, precio_max=999):
    """Lista juegos dentro de un rango de precio, de menor a mayor."""

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT j.juego_id,
               j.titulo,
               c.nombre                         AS categoria,
               j.precio,
               COUNT(DISTINCT b.usuario_id)     AS copias_vendidas
        FROM juegos j
        JOIN juegos_categorias jc ON j.juego_id     = jc.juego_id
        JOIN categorias c         ON jc.categoria_id = c.categoria_id
        LEFT JOIN biblioteca b    ON j.juego_id     = b.juego_id
        WHERE j.precio BETWEEN %s AND %s
        GROUP BY j.juego_id, j.titulo, c.nombre, j.precio
        ORDER BY j.precio ASC, copias_vendidas DESC
        """

        cursor.execute(query, (precio_min, precio_max))
        juegos = cursor.fetchall()

        print(f"\nJuegos entre ${precio_min:.2f} y ${precio_max:.2f}")
        print(f"{'─'*55}")
        for jid, titulo, cat, precio, ventas in juegos:
            print(f"  ${precio:>6.2f}  {titulo:<28} ({cat})  - {ventas:,} ventas")
        print(f"{'─'*55}")
        print(f"Total: {len(juegos)} juegos\n")

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

def mostrar_logros_usuario(usuario_id):
    """Logros desbloqueados por un usuario, con el juego al que pertenecen."""

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT j.titulo         AS juego,
               l.nombre         AS logro,
               l.descripcion,
               lu.fecha_desbloqueo
        FROM logros_usuarios lu
        JOIN logros  l ON lu.logro_id  = l.logro_id
        JOIN juegos  j ON l.juego_id   = j.juego_id
        WHERE lu.usuario_id = %s
        ORDER BY lu.fecha_desbloqueo DESC
        """

        cursor.execute(query, (usuario_id,))
        logros = cursor.fetchall()

        if not logros:
            print("Este usuario no tiene logros desbloqueados.")
            return []

        print(f"\nLogros del usuario {usuario_id}:")
        print(f"{'─'*60}")
        for juego, logro, descripcion, fecha in logros:
            print(f"[LOGRO] {logro}  ({juego})")
            print(f"   {descripcion or 'Sin descripcion'}  -  {fecha.strftime('%d/%m/%Y')}")
        print(f"{'─'*60}")
        print(f"Total: {len(logros)} logros\n")

        return logros

    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        connection.close()


def mostrar_resenas_juego(juego_id):
    """Reseñas de un juego con el nombre del usuario que las escribio."""

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT u.nombre_usuario,
               r.recomendado,
               r.contenido,
               r.fecha_publicacion
        FROM resenas r
        JOIN usuarios u ON r.usuario_id = u.usuario_id
        WHERE r.juego_id = %s
        ORDER BY r.fecha_publicacion DESC
        """

        cursor.execute(query, (juego_id,))
        resenas = cursor.fetchall()

        if not resenas:
            print("Este juego no tiene reseñas aun.")
            return []

        print(f"\nResenas del juego {juego_id}:")
        print(f"{'─'*55}")
        for nombre, recomendado, contenido, fecha in resenas:
            pulgar = "[+]" if recomendado else "[-]"
            print(f"{pulgar} {nombre}  -  {fecha.strftime('%d/%m/%Y')}")
            print(f"   {contenido}\n")
        print(f"{'─'*55}")
        print(f"Total: {len(resenas)} resenas\n")

        return resenas

    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        connection.close()


def promedio_calificaciones_juego(juego_id):
    """
    Promedio de aprobacion de un juego especifico
    con desglose de resenas positivas vs negativas.
    """

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT j.titulo,
               COUNT(r.resena_id)                                       AS total_resenas,
               SUM(CASE WHEN r.recomendado THEN 1 ELSE 0 END)          AS positivas,
               SUM(CASE WHEN NOT r.recomendado THEN 1 ELSE 0 END)      AS negativas,
               ROUND(
                   AVG(CASE WHEN r.recomendado THEN 1.0 ELSE 0.0 END) * 100, 2
               )                                                        AS aprobacion_pct
        FROM juegos j
        LEFT JOIN resenas r ON j.juego_id = r.juego_id
        WHERE j.juego_id = %s
        GROUP BY j.juego_id, j.titulo
        """

        cursor.execute(query, (juego_id,))
        fila = cursor.fetchone()

        if not fila:
            print("Juego no encontrado.")
            return None

        titulo, total, pos, neg, aprob = fila

        print(f"\nCalificaciones de: {titulo}")
        print(f"{'─'*40}")
        print(f"  Total resenas  : {total or 0}")
        print(f"  Positivas [+]  : {pos or 0}")
        print(f"  Negativas [-]  : {neg or 0}")
        print(f"  Aprobacion     : {aprob or 0:.2f}%")
        print(f"{'─'*40}\n")

        return fila

    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        connection.close()


def ranking_juegos_mejor_calificados(minimo_resenas=5, limite=10):
    """
    Ranking de juegos mejor calificados.
    Se filtra por minimo de resenas para que sea estadisticamente valido.
    """

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT j.juego_id,
               j.titulo,
               c.nombre                                                 AS categoria,
               j.precio,
               COUNT(r.resena_id)                                       AS total_resenas,
               ROUND(
                   AVG(CASE WHEN r.recomendado THEN 1.0 ELSE 0.0 END) * 100, 1
               )                                                        AS aprobacion_pct
        FROM juegos j
        JOIN juegos_categorias jc ON j.juego_id     = jc.juego_id
        JOIN categorias c         ON jc.categoria_id = c.categoria_id
        LEFT JOIN resenas r       ON j.juego_id     = r.juego_id
        GROUP BY j.juego_id, j.titulo, c.nombre, j.precio
        HAVING COUNT(r.resena_id) >= %s
        ORDER BY aprobacion_pct DESC, total_resenas DESC
        LIMIT %s
        """

        cursor.execute(query, (minimo_resenas, limite))
        resultados = cursor.fetchall()

        print(f"\nTOP {limite} JUEGOS MEJOR CALIFICADOS (min. {minimo_resenas} resenas)")
        print(f"{'─'*65}")
        print(f"{'#':<4} {'Título':<28} {'Categoría':<13} {'Precio':>7}  {'Resenas':>8}  Aprob.")
        print(f"{'─'*65}")
        for rank, (jid, titulo, cat, precio, resenas, aprob) in enumerate(resultados, 1):
            print(f"{rank:<4} {titulo:<28} {cat:<13} ${precio:>6.2f}  {resenas:>8,}  {aprob:.1f}%")
        print(f"{'─'*65}\n")

        return resultados

    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        connection.close()


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


def mostrar_lista_deseos(usuario_id):
    """Juegos en la lista de deseos de un usuario."""

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT j.juego_id,
               j.titulo,
               c.nombre    AS categoria,
               j.precio,
               ld.fecha_agregado
        FROM lista_deseos ld
        JOIN juegos j             ON ld.juego_id    = j.juego_id
        JOIN juegos_categorias jc ON j.juego_id     = jc.juego_id
        JOIN categorias c         ON jc.categoria_id = c.categoria_id
        WHERE ld.usuario_id = %s
        ORDER BY ld.fecha_agregado DESC
        """

        cursor.execute(query, (usuario_id,))
        deseos = cursor.fetchall()

        if not deseos:
            print("La lista de deseos esta vacia.")
            return []

        print(f"\nLista de deseos del usuario {usuario_id}:")
        print(f"{'─'*55}")
        for juego_id, titulo, categoria, precio, fecha in deseos:
            print(f"  [{juego_id}] {titulo:<25} {categoria:<12} ${precio:.2f}")
        print(f"{'─'*55}")
        print(f"Total: {len(deseos)} juegos\n")

        return deseos

    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        connection.close()


# ══════════════════════════════════════════════
#  HISTORIAL DE COMPRAS
# ══════════════════════════════════════════════

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


# ══════════════════════════════════════════════
#  FEED DE LA TIENDA
# ══════════════════════════════════════════════

def feed_juegos_mas_vendidos(limite=10):
    """
    Pantalla principal de la tienda.
    Juegos ordenados por copias vendidas, con aprobacion e ingresos.
    """

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT j.juego_id,
               j.titulo,
               c.nombre                                                  AS categoria,
               j.precio,
               COUNT(DISTINCT b.usuario_id)                              AS copias_vendidas,
               COALESCE(COUNT(r.resena_id), 0)                           AS total_resenas,
               ROUND(
                   AVG(CASE WHEN r.recomendado THEN 1.0 ELSE 0.0 END) * 100, 1
               )                                                         AS aprobacion_pct,
               SUM(t.monto_total)                                        AS ingresos_totales
        FROM juegos j
        JOIN juegos_categorias jc ON j.juego_id     = jc.juego_id
        JOIN categorias c         ON jc.categoria_id = c.categoria_id
        LEFT JOIN biblioteca b    ON j.juego_id     = b.juego_id
        LEFT JOIN resenas r       ON j.juego_id     = r.juego_id
        LEFT JOIN transacciones t ON t.usuario_id   = b.usuario_id
        GROUP BY j.juego_id, j.titulo, c.nombre, j.precio
        ORDER BY copias_vendidas DESC
        LIMIT %s
        """

        cursor.execute(query, (limite,))
        resultados = cursor.fetchall()

        print(f"\n{'═'*80}")
        print(f"  FEED DE LA TIENDA - TOP {limite} JUEGOS MAS VENDIDOS")
        print(f"{'═'*80}")
        print(f"{'#':<4} {'Título':<26} {'Categoría':<13} {'Precio':>7}  "
              f"{'Ventas':>7}  {'Aprob.':>7}  Ingresos")
        print(f"{'─'*80}")
        for rank, (jid, titulo, cat, precio, ventas, resenas, aprob, ingresos) in \
                enumerate(resultados, 1):
            aprob_str = f"{aprob:.1f}%" if aprob is not None else "N/A"
            ingr_str  = f"${ingresos:,.2f}" if ingresos else "$0.00"
            print(f"{rank:<4} {titulo:<26} {cat:<13} ${precio:>6.2f}  "
                  f"{ventas:>7,}  {aprob_str:>7}  {ingr_str}")
        print(f"{'═'*80}\n")

        return resultados

    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        connection.close()


# ══════════════════════════════════════════════
#  REPORTES
# ══════════════════════════════════════════════
