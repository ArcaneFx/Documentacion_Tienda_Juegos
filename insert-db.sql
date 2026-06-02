TRUNCATE usuarios, juegos, categorias, metodos_pago, transacciones, biblioteca, 
logros, logros_usuarios, resenas, lista_deseos, carrito_compras, juegos_categorias RESTART IDENTITY CASCADE;

DO $$
DECLARE

    v_total_usuarios      INT := 500; 
    v_total_juegos        INT := 100;
    v_transacciones_total INT := 40000; 

    -- nombres aleatorios
    nombres_usr    TEXT[] := ARRAY['Jason', 'Mayra', 'Alex', 'Elena', 'Lucas', 'Sofi', 'Nico', 'Valu', 'Diego', 'Ana'];
    titulos_juego  TEXT[] := ARRAY['Shadow', 'Cyber', 'Eternal', 'Lost', 'Dark', 'Dragon', 'Super', 'Space', 'Final', 'Mega'];
    sustantivos_j  TEXT[] := ARRAY['Hunter', 'Quest', 'Legacy', 'World', 'Legends', 'War', 'Strike', 'Knight', 'Origin'];
    
    -- logros personalizado
    nombres_logro  TEXT[] := ARRAY['Primeros Pasos', 'Fuera del Cascarón', 'Aprendiz de Héroe', 'Bienvenido al Mundo',
                                  'El Comienzo del Fin', 'Recién Llegado', 'Sangre Nueva', 'Imparable', 'Ojo de Halcón', 
                                  'Furia Desatada', 'Último Hombre en Pie', 'Maestro de Armas', 'Reflejos de Rayo', 
                                  'Verdugo del Mal', 'Trotamundos', 'Cartógrafo Real', 'Cazador de Secretos', 
                                  'Bajo la Piedra', 'Turista del Caos', 'No todo el que vaga está perdido', 
                                  'Horizonte Lejano', 'Bolsillos Llenos', 'Rey de la Chatarra', 'Avaro por Naturaleza', 
                                  'El Dorado', 'Coleccionista de Sombras', 'Urraca Plateada', 'Fortuna Incalculable', 
                                  'Leyenda Viviente', 'Desafiando al Destino', 'Hijo de la Tormenta', 'Soberano del Tiempo', 
                                  'Más allá del Deber', 'Cero Errores', 'El Elegido', 'Rompedor de Cadenas', 
                                  '¿Cómo hiciste eso?', 'Suerte de Principiante', 'Modo Dios', 'Paciencia Infinita', 
                                  'Rompejuegos', 'Fanático Número Uno', 'Crítico de Artefactos'];
    
    v_u_id         INT;
    v_j_id         INT;
    v_l_id         INT;
    v_fecha        TIMESTAMP;
    v_precio       DECIMAL;
    i              INT;
    j              INT;
BEGIN

    INSERT INTO categorias (nombre) 
    SELECT unnest(ARRAY['Acción', 'RPG', 'Indie', 'Estrategia', 'Terror', 'Deportes', 'Simulación', 'Aventura']);

    -- Usuario y metodos de pago
    FOR i IN 1..v_total_usuarios LOOP
        INSERT INTO usuarios (nombre_usuario, correo_electronico, contrasena_hash, saldo_cartera)
        VALUES (
            (nombres_usr[1 + floor(random() * array_length(nombres_usr, 1))]) || i || floor(random()*99),
            'estudiante' || i || '@uach.cl',
            'pwhash_' || i,
            random() * 100
        ) RETURNING usuario_id INTO v_u_id;

        INSERT INTO metodos_pago (usuario_id, proveedor, ultimos_cuatro_digitos, es_predeterminado)
        VALUES (v_u_id, 'Visa/MasterCard', floor(1000 + random() * 8999)::TEXT, TRUE);
    END LOOP;

    -- Juegos y logros
    FOR i IN 1..v_total_juegos LOOP
        v_precio := (ARRAY[0, 9.99, 14.99, 19.99, 29.99, 59.99])[1 + floor(random() * 6)];
        
        INSERT INTO juegos (titulo, descripcion, precio, fecha_lanzamiento, desarrollador)
        VALUES (
            (titulos_juego[1 + floor(random() * array_length(titulos_juego, 1))]) || ' ' || 
            (sustantivos_j[1 + floor(random() * array_length(sustantivos_j, 1))]),
            'Una épica aventura desarrollada por Estudio ' || i,
            v_precio,
            '2021-01-01'::DATE + (random() * 1000 || ' days')::INTERVAL,
            'Desarrollador Austral'
        ) RETURNING juego_id INTO v_j_id;

        -- Crear 3 logros aleatorios
        FOR j IN 1..3 LOOP
            INSERT INTO logros (juego_id, nombre, descripcion)
            VALUES (
                v_j_id, 
                nombres_logro[1 + floor(random() * array_length(nombres_logro, 1))],
                'Descripción del desafío para el juego ' || v_j_id
            );
        END LOOP;

        INSERT INTO juegos_categorias (juego_id, categoria_id)
        VALUES (v_j_id, 1 + floor(random() * 8));
    END LOOP;

    -- Simulacion de transacciones y actividad
    FOR i IN 1..v_transacciones_total LOOP
        v_u_id := 1 + floor(random() * v_total_usuarios);
        v_j_id := 1 + floor(random() * v_total_juegos);
        v_fecha := '2023-01-01'::TIMESTAMP + (random() * (interval '1210 days'));
        
        SELECT precio INTO v_precio FROM juegos WHERE juego_id = v_j_id;

        -- Venta y Biblioteca
        INSERT INTO transacciones (usuario_id, metodo_pago_id, monto_total, fecha_transaccion)
        VALUES (v_u_id, v_u_id, v_precio, v_fecha);

        INSERT INTO biblioteca (usuario_id, juego_id, fecha_compra, tiempo_jugado_minutos)
        VALUES (v_u_id, v_j_id, v_fecha, floor(random() * 8000))
        ON CONFLICT DO NOTHING;

        -- Desbloqueo de logros
        IF random() < 0.5 THEN
            SELECT logro_id INTO v_l_id FROM logros WHERE juego_id = v_j_id ORDER BY random() LIMIT 1;
            IF v_l_id IS NOT NULL THEN
                INSERT INTO logros_usuarios (usuario_id, logro_id, fecha_desbloqueo)
                VALUES (v_u_id, v_l_id, v_fecha + (random() * interval '5 days'))
                ON CONFLICT DO NOTHING;
            END IF;
        END IF;

        -- Reseñas
        IF random() < 0.1 THEN
            INSERT INTO resenas (usuario_id, juego_id, contenido, recomendado)
            VALUES (v_u_id, v_j_id, 'Comentario automático del usuario ' || v_u_id, (random() > 0.1));
        END IF;
    END LOOP;

    RAISE NOTICE '✔ Datos cargados con logros personalizados: % transacciones.', v_transacciones_total;
END;
$$;





---------------------
--prueba de datos
---------------------

SELECT EXTRACT(YEAR FROM fecha_transaccion) AS anio, SUM(monto_total) 
FROM transacciones 
GROUP BY anio ORDER BY anio;



SELECT u.nombre_usuario, SUM(b.tiempo_jugado_minutos) 
FROM usuarios u 
JOIN biblioteca b ON u.usuario_id = b.usuario_id 
GROUP BY u.nombre_usuario 
ORDER BY 2 DESC LIMIT 10
;


SELECT 'Usuarios' as Tabla, COUNT(*) as Total FROM usuarios
UNION ALL SELECT 'Juegos', COUNT(*) FROM juegos
UNION ALL SELECT 'Ventas', COUNT(*) FROM transacciones
UNION ALL SELECT 'Logros Obtenidos', COUNT(*) FROM logros_usuarios;

SELECT 
    EXTRACT(YEAR FROM fecha_transaccion) AS anio,
    COUNT(*) AS num_ventas,
    SUM(monto_total) AS ingresos_totales
	FROM transacciones
	GROUP BY anio
	ORDER BY anio;

SELECT 
    j.titulo,
    COUNT(b.usuario_id) AS copias_vendidas,
    COUNT(r.resena_id) AS cantidad_resenas,
    ROUND(AVG(CASE WHEN r.recomendado THEN 1 ELSE 0 END) * 100, 2) AS porcentaje_aprobacion
	FROM juegos j
	LEFT JOIN biblioteca b ON j.juego_id = b.juego_id
	LEFT JOIN resenas r ON j.juego_id = r.juego_id
	GROUP BY j.juego_id, j.titulo
	ORDER BY copias_vendidas DESC
	LIMIT 5;


SELECT 
    u.nombre_usuario,
    j.titulo AS juego,
    l.nombre AS nombre_logro,
    lu.fecha_desbloqueo
FROM logros_usuarios lu
JOIN usuarios u ON lu.usuario_id = u.usuario_id
JOIN logros l ON lu.logro_id = l.logro_id
JOIN juegos j ON l.juego_id = j.juego_id
ORDER BY lu.fecha_desbloqueo DESC
LIMIT 10;


SELECT 
    u.nombre_usuario,
    COUNT(t.transaccion_id) AS compras_realizadas,
    SUM(t.monto_total) AS total_invertido
FROM usuarios u
JOIN transacciones t ON u.usuario_id = t.usuario_id
GROUP BY u.usuario_id, u.nombre_usuario
HAVING SUM(t.monto_total) > 100
ORDER BY total_invertido DESC;


SELECT 'Transacciones Totales' AS Concepto, COUNT(*) AS Cantidad FROM transacciones
UNION ALL
SELECT 'Juegos en Bibliotecas', COUNT(*) FROM biblioteca
UNION ALL
SELECT 'Logros Desbloqueados', COUNT(*) FROM logros_usuarios;

SELECT 
    t.transaccion_id, 
    u.nombre_usuario, 
    j.titulo AS juego_comprado, 
    t.monto_total, 
    mp.proveedor AS metodo_usado, 
    t.fecha_transaccion
FROM transacciones t
JOIN usuarios u ON t.usuario_id = u.usuario_id
JOIN metodos_pago mp ON t.metodo_pago_id = mp.metodo_pago_id
JOIN juegos j ON j.juego_id = (SELECT b.juego_id FROM biblioteca b WHERE b.usuario_id = u.usuario_id LIMIT 1)
LIMIT 10;


SELECT 
    c.nombre AS categoria, 
    COUNT(t.transaccion_id) AS total_ventas,
    SUM(t.monto_total) AS recaudacion
FROM categorias c
JOIN juegos_categorias jc ON c.categoria_id = jc.categoria_id
JOIN juegos j ON jc.juego_id = j.juego_id
JOIN transacciones t ON j.juego_id = j.juego_id -- Relación lógica
GROUP BY c.nombre
ORDER BY recaudacion DESC;

#PRUEBAAAAAAAAAAAA

SELECT usuario_id, nombre_usuario, correo_electronico, contrasena_hash, saldo_cartera 
FROM usuarios 
ORDER BY usuario_id DESC 
LIMIT 5;

SELECT t.transaccion_id, u.nombre_usuario, t.monto_total, t.fecha_transaccion
FROM transacciones t
JOIN usuarios u ON t.usuario_id = u.usuario_id
WHERE t.transaccion_id = 40001;

SELECT b.usuario_id, u.nombre_usuario, j.titulo AS juego_poseido, b.fecha_compra
FROM biblioteca b
JOIN usuarios u ON b.usuario_id = u.usuario_id
JOIN juegos j ON b.juego_id = j.juego_id
WHERE u.nombre_usuario = 'yughiku';

DELETE FROM carrito_compras WHERE usuario_id = (SELECT usuario_id FROM usuarios WHERE nombre_usuario = 'yughiku');

-- 2. Borramos el juego que quedó asociado en su biblioteca
DELETE FROM biblioteca WHERE usuario_id = (SELECT usuario_id FROM usuarios WHERE nombre_usuario = 'yughiku');

-- 3. Borramos la boleta N° 40001 que generó en las transacciones
DELETE FROM transacciones WHERE transaccion_id = 40001;

-- 4. Ahora que ya no tiene compras ni amarras, borramos al usuario maestro
DELETE FROM usuarios WHERE nombre_usuario = 'yughiku';


