# etl.py
# Proceso ETL: carga el modelo estrella (esquema dw) a partir
# de las tablas transaccionales (esquema public).
#
# Estrategia: RECARGA COMPLETA (full refresh).
#   Cada ejecución vacía las tablas dw y las vuelve a llenar.
#   Esto hace que el script se pueda correr cuantas veces se
#   quiera (idempotente), lo cual es necesario para automatizarlo
#   con cron / Task Scheduler.
#
# La Transformación ocurre DENTRO de cada SELECT (calcular el año,
# armar el rango de saldo, derivar la clave de tiempo, etc.).
#
# Uso:
#   python etl.py

from database import get_db_connection


# ──────────────────────────────────────────────────────────────
#  SENTENCIAS SQL DEL ETL
# ──────────────────────────────────────────────────────────────

# Vaciar las tablas dw. Primero los hechos (tienen FK hacia las
# dimensiones), luego las dimensiones. RESTART IDENTITY reinicia
# el contador venta_id.
SQL_LIMPIAR = """
TRUNCATE dw.hechos_ventas,
         dw.dim_tiempo,
         dw.dim_juego,
         dw.dim_usuario,
         dw.dim_metodo_pago
RESTART IDENTITY CASCADE;
"""

# DIMENSIÓN TIEMPO
# Se pre-genera una fila por cada día de un rango fijo y amplio
# (2020-2027) para garantizar que TODA fecha de compra tenga su
# clave, incluso compras nuevas hechas desde la app. Clave YYYYMMDD.
# (TM = nombre de mes/día en el idioma del servidor PostgreSQL)
SQL_DIM_TIEMPO = """
INSERT INTO dw.dim_tiempo
    (tiempo_id, fecha, anio, trimestre, mes, nombre_mes,
     dia, dia_semana, nombre_dia, es_fin_semana)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INT,
    d::DATE,
    EXTRACT(YEAR    FROM d)::INT,
    EXTRACT(QUARTER FROM d)::INT,
    EXTRACT(MONTH   FROM d)::INT,
    TRIM(TO_CHAR(d, 'TMMonth')),
    EXTRACT(DAY     FROM d)::INT,
    EXTRACT(DOW     FROM d)::INT,
    TRIM(TO_CHAR(d, 'TMDay')),
    EXTRACT(DOW FROM d) IN (0, 6)
FROM generate_series(
        '2020-01-01'::DATE,
        '2027-12-31'::DATE,
        INTERVAL '1 day'
     ) AS g(d);
"""

# DIMENSIÓN JUEGO
# La categoría se DENORMALIZA (se trae adentro de la dimensión).
# El LATERAL ... LIMIT 1 garantiza una sola categoría por juego,
# así no se duplican filas si un juego tuviera más de una.
SQL_DIM_JUEGO = """
INSERT INTO dw.dim_juego
    (juego_id, titulo, categoria, desarrollador, editor,
     precio, fecha_lanzamiento)
SELECT
    j.juego_id,
    j.titulo,
    c.nombre,
    j.desarrollador,
    j.editor,
    j.precio,
    j.fecha_lanzamiento
FROM juegos j
LEFT JOIN LATERAL (
    SELECT cat.nombre
    FROM juegos_categorias jc
    JOIN categorias cat ON jc.categoria_id = cat.categoria_id
    WHERE jc.juego_id = j.juego_id
    LIMIT 1
) c ON TRUE;
"""

# DIMENSIÓN USUARIO
# Se derivan dos atributos nuevos: el año de registro y un
# bucket (rango) del saldo, útil para segmentar en el análisis.
SQL_DIM_USUARIO = """
INSERT INTO dw.dim_usuario
    (usuario_id, nombre_usuario, correo, anio_registro, rango_saldo)
SELECT
    u.usuario_id,
    u.nombre_usuario,
    u.correo_electronico,
    EXTRACT(YEAR FROM u.fecha_registro)::INT,
    CASE
        WHEN u.saldo_cartera = 0   THEN 'Sin saldo'
        WHEN u.saldo_cartera < 50  THEN 'Bajo'
        WHEN u.saldo_cartera < 100 THEN 'Medio'
        ELSE 'Alto'
    END
FROM usuarios u;
"""

# DIMENSIÓN MÉTODO DE PAGO
SQL_DIM_METODO = """
INSERT INTO dw.dim_metodo_pago (metodo_pago_id, proveedor)
SELECT metodo_pago_id, proveedor
FROM metodos_pago;
"""

# TABLA DE HECHOS: VENTAS
# Grano = una compra de un juego (una fila de biblioteca).
#   - monto      : se toma del precio del juego
#   - tiempo_id  : se deriva de fecha_compra (YYYYMMDD)
#   - metodo_pago: el método del usuario (LATERAL ... LIMIT 1)
SQL_HECHOS = """
INSERT INTO dw.hechos_ventas
    (tiempo_id, juego_id, usuario_id, metodo_pago_id,
     monto, cantidad, tiempo_jugado_minutos)
SELECT
    TO_CHAR(b.fecha_compra, 'YYYYMMDD')::INT,
    b.juego_id,
    b.usuario_id,
    mp.metodo_pago_id,
    j.precio,
    1,
    b.tiempo_jugado_minutos
FROM biblioteca b
JOIN juegos j ON b.juego_id = j.juego_id
LEFT JOIN LATERAL (
    SELECT metodo_pago_id
    FROM metodos_pago
    WHERE usuario_id = b.usuario_id
    LIMIT 1
) mp ON TRUE;
"""

# Orden de carga: dimensiones primero, hechos al final (por las FK).
PASOS = [
    ("dim_tiempo",      SQL_DIM_TIEMPO),
    ("dim_juego",       SQL_DIM_JUEGO),
    ("dim_usuario",     SQL_DIM_USUARIO),
    ("dim_metodo_pago", SQL_DIM_METODO),
    ("hechos_ventas",   SQL_HECHOS),
]


# ──────────────────────────────────────────────────────────────
#  PROCESO PRINCIPAL
# ──────────────────────────────────────────────────────────────

def ejecutar_etl():
    print("\n========================================")
    print("  PROCESO ETL: OLTP (public) -> OLAP (dw)")
    print("========================================\n")

    conn = get_db_connection()
    if conn is None:
        print("No se pudo conectar a la base de datos.")
        return

    cur = conn.cursor()
    try:
        print("1. Vaciando tablas del modelo estrella...")
        cur.execute(SQL_LIMPIAR)

        print("2. Cargando dimensiones y hechos:")
        for nombre, sql in PASOS:
            cur.execute(sql)
            print(f"   - {nombre:<16}: {cur.rowcount:>7,} filas")

        # Si todo salió bien, se confirma la carga completa
        conn.commit()

        # Resumen final (sirve de evidencia para la presentacion)
        print("\n----------------------------------------")
        print("  RESUMEN DEL DATA WAREHOUSE (dw)")
        print("----------------------------------------")
        for tabla in ["dim_tiempo", "dim_juego", "dim_usuario",
                      "dim_metodo_pago", "hechos_ventas"]:
            cur.execute(f"SELECT COUNT(*) FROM dw.{tabla}")
            total = cur.fetchone()[0]
            print(f"  {tabla:<18}: {total:>7,} filas")
        print("----------------------------------------")
        print("  Carga completada exitosamente.\n")

    except Exception as error:
        # Si algo falla, se revierte TODA la carga (atomicidad)
        conn.rollback()
        print(f"\nError durante el ETL (se revirtieron los cambios): {error}")

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    ejecutar_etl()