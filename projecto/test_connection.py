from database import get_db_connection

try:
    conn = get_db_connection()

    print("Conexión exitosa")

    cursor = conn.cursor()
    #consulta sql
    query = """
    SELECT u.nombre_usuario,
            SUM(b.tiempo_jugado_minutos) AS total_minutos
    FROM usuarios u
    JOIN biblioteca b
        ON u.usuario_id = b.usuario_id
    GROUP BY u.nombre_usuario
    ORDER BY total_minutos DESC
    LIMIT 10;
    """

    #ejecutar consulta
    cursor.execute(query)

    #obtener resultados
    resultados = cursor.fetchall()

    #mostrar resultados
    print("TOP 10 JUGADORES\n")

    for usuario, minutos in resultados:
        print(f"{usuario}: {minutos} minutos")


    cursor.close()
    conn.close()

except Exception as e:
    print("Error:", e)  