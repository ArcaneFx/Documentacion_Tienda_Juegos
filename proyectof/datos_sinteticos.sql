-- Activar extensión necesaria para encriptar contraseñas con crypt()/gen_salt()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

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
    v_mp_id        INT;
    v_fecha        TIMESTAMP;
    v_precio       DECIMAL;
    i              INT;
    j              INT;

    -- arreglo para mapear usuario_id -> metodo_pago_id
    metodos_pago_ids INT[] := ARRAY[]::INT[];
BEGIN

    INSERT INTO categorias (nombre) 
    SELECT unnest(ARRAY['Acción', 'RPG', 'Indie', 'Estrategia', 'Terror', 'Deportes', 'Simulación', 'Aventura']);

    -- Usuario y metodos de pago
    FOR i IN 1..v_total_usuarios LOOP
        INSERT INTO usuarios (nombre_usuario, correo_electronico, contrasena_hash, saldo_cartera)
        VALUES (
            (nombres_usr[1 + floor(random() * array_length(nombres_usr, 1))]) || i || floor(random()*99),
            'estudiante' || i || '@uach.cl',
            crypt('pwhash_' || i, gen_salt('bf')),
            random() * 100
        ) RETURNING usuario_id INTO v_u_id;

        INSERT INTO metodos_pago (usuario_id, proveedor, ultimos_cuatro_digitos, es_predeterminado)
        VALUES (v_u_id, 'Visa/MasterCard', floor(1000 + random() * 8999)::TEXT, TRUE)
        RETURNING metodo_pago_id INTO v_mp_id;

        -- guardar el metodo_pago_id en el arreglo (indice = usuario_id)
        metodos_pago_ids[v_u_id] := v_mp_id;
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
        v_fecha := '2021-01-01'::TIMESTAMP + (random() * (interval '1460 days'));
        
        SELECT precio INTO v_precio FROM juegos WHERE juego_id = v_j_id;

        -- Venta y Biblioteca (usa el metodo_pago_id correcto del usuario)
        INSERT INTO transacciones (usuario_id, metodo_pago_id, monto_total, fecha_transaccion)
        VALUES (v_u_id, metodos_pago_ids[v_u_id], v_precio, v_fecha);

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
