
-- Credenciales para login:
--   Usuario: arkantosalmirante  | Contraseña: almirantesenior
--   Usuario: panxocloloco        | Contraseña: panxoxo
--   Usuario: chuckmcgill         | Contraseña: estadisticopesao
-- =====================================================

--------------------------------------------------------
-- 1. CREAR USUARIOS (hash bcrypt generado con Python)
--------------------------------------------------------

INSERT INTO usuarios (
    nombre_usuario,
    correo_electronico,
    contrasena_hash,
    saldo_cartera
)
VALUES
(
    'arkantosalmirante',
    'arkantosalmirante@demo.cl',
    '$2b$12$iEKyqjFMkDA5YPg8meEv9.tyiYI7HnrU2m1boQOT7ld1a3Z0XHd/W',
    0.00
),
(
    'panxocloloco',
    'panxocloloco@demo.cl',
    '$2b$12$B79KQNyqUjfq1BOLZQQo0unR8ufxfaK1h72Wu0Clngm5uKMQHw.xa',
    25.50
),
(
    'chuckmcgill',
    'chuckmcgill@demo.cl',
    '$2b$12$vaiZNSoWH5HkQOMgmkvRMulQom09AdEuQT9018fn626NJ79n9Nu7u',
    500.00
);

--------------------------------------------------------
-- 2. MÉTODOS DE PAGO
--------------------------------------------------------

INSERT INTO metodos_pago (
    usuario_id,
    proveedor,
    ultimos_cuatro_digitos,
    es_predeterminado
)
VALUES
(501,'Visa','1234',TRUE),
(502,'MasterCard','5678',TRUE),
(503,'Visa','9999',TRUE);

--------------------------------------------------------
-- 3. BIBLIOTECA
--------------------------------------------------------

-- panxocloloco
INSERT INTO biblioteca (
    usuario_id,
    juego_id,
    fecha_compra,
    tiempo_jugado_minutos,
    ultima_vez_jugado
)
VALUES
(502,3,'2025-12-15',120,'2026-05-25'),
(502,8,'2026-01-10',350,'2026-05-30');

-- chuckmcgill
INSERT INTO biblioteca (
    usuario_id,
    juego_id,
    fecha_compra,
    tiempo_jugado_minutos,
    ultima_vez_jugado
)
VALUES
(503,1 ,'2024-01-10',8000,'2026-05-30'),
(503,2 ,'2024-02-10',5500,'2026-05-29'),
(503,4 ,'2024-03-15',7200,'2026-05-28'),
(503,5 ,'2024-05-01',6100,'2026-05-31'),
(503,7 ,'2024-07-12',9000,'2026-05-30'),
(503,10,'2025-01-01',4200,'2026-05-20');

--------------------------------------------------------
-- 4. TRANSACCIONES
--------------------------------------------------------

INSERT INTO transacciones (
    usuario_id,
    metodo_pago_id,
    monto_total,
    estado,
    fecha_transaccion
)
VALUES

-- panxocloloco
(502,502,14.99,'completado','2025-12-15'),
(502,502,19.99,'completado','2026-01-10'),

-- chuckmcgill
(503,503,59.99,'completado','2024-01-10'),
(503,503,29.99,'completado','2024-02-10'),
(503,503,19.99,'completado','2024-03-15'),
(503,503,9.99 ,'completado','2024-05-01'),
(503,503,59.99,'completado','2024-07-12'),
(503,503,29.99,'completado','2025-01-01');

--------------------------------------------------------
-- 5. LOGROS
--------------------------------------------------------

-- panxocloloco: 2 logros del juego 3
INSERT INTO logros_usuarios (usuario_id, logro_id)
SELECT 502, logro_id
FROM logros
WHERE juego_id = 3
ORDER BY logro_id
LIMIT 2;

-- panxocloloco: 1 logro del juego 8
INSERT INTO logros_usuarios (usuario_id, logro_id)
SELECT 502, logro_id
FROM logros
WHERE juego_id = 8
ORDER BY logro_id
LIMIT 1;

-- chuckmcgill: todos los logros de los juegos que posee
INSERT INTO logros_usuarios (
    usuario_id,
    logro_id
)
SELECT
    503,
    logro_id
FROM logros
WHERE juego_id IN (1,2,4,5,7,10);

--------------------------------------------------------
-- 6. RESEÑAS
--------------------------------------------------------

INSERT INTO resenas (
    usuario_id,
    juego_id,
    contenido,
    recomendado
)
VALUES
(
    502,
    3,
    'Buen juego para pasar el rato.',
    TRUE
),
(
    503,
    1,
    'Uno de los mejores juegos que he probado.',
    TRUE
),
(
    503,
    7,
    'Excelente duración y rejugabilidad.',
    TRUE
);

--------------------------------------------------------
-- 7. LISTA DE DESEOS
--------------------------------------------------------

INSERT INTO lista_deseos (
    usuario_id,
    juego_id
)
VALUES
(501,1),
(501,2),
(501,3),
(502,10);

--------------------------------------------------------
-- 8. CARRITO DE COMPRAS
--------------------------------------------------------

INSERT INTO carrito_compras (
    usuario_id,
    juego_id
)
VALUES
(501,5),
(501,8);

--------------------------------------------------------
-- 9. VERIFICACIÓN
--------------------------------------------------------

SELECT
    u.usuario_id,
    u.nombre_usuario,
    u.saldo_cartera,
    COUNT(DISTINCT b.juego_id) AS juegos,
    COUNT(DISTINCT lu.logro_id) AS logros,
    COUNT(DISTINCT t.transaccion_id) AS compras
FROM usuarios u
LEFT JOIN biblioteca b
    ON u.usuario_id = b.usuario_id
LEFT JOIN logros_usuarios lu
    ON u.usuario_id = lu.usuario_id
LEFT JOIN transacciones t
    ON u.usuario_id = t.usuario_id
WHERE u.usuario_id >= 501
GROUP BY
    u.usuario_id,
    u.nombre_usuario,
    u.saldo_cartera
ORDER BY u.usuario_id;
