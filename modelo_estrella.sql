-- ============================================================
--  MODELO ESTRELLA (OLAP) - Tienda de Videojuegos
--  Asignatura: Bases de Datos
--
--  Proceso de negocio modelado : VENTAS de juegos
--  Grano de la tabla de hechos  : una compra de un juego,
--                                 por un usuario, en una fecha
--
--  NOTA DE DISEÑO:
--  En el OLTP la tabla 'transacciones' guarda el monto pero NO
--  tiene juego_id. El vínculo usuario-juego-fecha vive en la
--  tabla 'biblioteca'. Por eso el ETL construye los hechos desde
--  'biblioteca', tomando el monto desde 'juegos.precio'.
-- ============================================================

-- Esquema separado para mantener OLTP y OLAP independientes.
CREATE SCHEMA IF NOT EXISTS dw;


-- Se elimina primero la tabla de hechos por las claves foráneas,
-- luego las dimensiones.
DROP TABLE IF EXISTS dw.hechos_ventas    CASCADE;
DROP TABLE IF EXISTS dw.dim_tiempo        CASCADE;
DROP TABLE IF EXISTS dw.dim_juego         CASCADE;
DROP TABLE IF EXISTS dw.dim_usuario       CASCADE;
DROP TABLE IF EXISTS dw.dim_metodo_pago   CASCADE;


-- ------------------------------------------------------------
--  DIMENSIÓN TIEMPO
--  Clave inteligente con formato YYYYMMDD (ej. 20240315).
--  Así el ETL no necesita un lookup: la clave se deriva
--  directamente de la fecha de cada venta.
-- ------------------------------------------------------------
CREATE TABLE dw.dim_tiempo (
    tiempo_id      INT PRIMARY KEY,          -- formato YYYYMMDD
    fecha          DATE        NOT NULL,
    anio           INT         NOT NULL,
    trimestre      INT         NOT NULL,     -- 1..4
    mes            INT         NOT NULL,     -- 1..12
    nombre_mes     VARCHAR(15) NOT NULL,
    dia            INT         NOT NULL,
    dia_semana     INT         NOT NULL,     -- 0=domingo .. 6=sabado
    nombre_dia     VARCHAR(15) NOT NULL,
    es_fin_semana  BOOLEAN     NOT NULL
);


-- ------------------------------------------------------------
--  DIMENSIÓN JUEGO
--  La categoría va DENORMALIZADA dentro de esta tabla.
--  Eso es lo que hace que el modelo sea ESTRELLA y no copo
--  de nieve (no se cuelga 'categorias' como tabla aparte).
-- ------------------------------------------------------------
CREATE TABLE dw.dim_juego (
    juego_id           INT PRIMARY KEY,      -- clave natural desde OLTP
    titulo             VARCHAR(100) NOT NULL,
    categoria          VARCHAR(50),          -- denormalizada
    desarrollador      VARCHAR(100),
    editor             VARCHAR(100),
    precio             DECIMAL(10,2),
    fecha_lanzamiento  DATE
);


-- ------------------------------------------------------------
--  DIMENSIÓN USUARIO
--  Se agregan atributos derivados útiles para el análisis:
--  anio_registro y un rango/bucket de saldo.
-- ------------------------------------------------------------
CREATE TABLE dw.dim_usuario (
    usuario_id      INT PRIMARY KEY,
    nombre_usuario  VARCHAR(50),
    correo          VARCHAR(100),
    anio_registro   INT,
    rango_saldo     VARCHAR(20)              -- 'Sin saldo','Bajo','Medio','Alto'
);


-- ------------------------------------------------------------
--  DIMENSIÓN MÉTODO DE PAGO
--  Dimensión pequeña: permite analizar ventas por proveedor.
-- ------------------------------------------------------------
CREATE TABLE dw.dim_metodo_pago (
    metodo_pago_id  INT PRIMARY KEY,
    proveedor       VARCHAR(20)
);


-- ------------------------------------------------------------
--  TABLA DE HECHOS: VENTAS
--  Larga y angosta: solo claves foráneas + medidas numéricas.
--
--  Tipos de medida:
--    monto                 -> aditiva       (se puede sumar siempre)
--    cantidad              -> aditiva       (conteo de ventas)
--    tiempo_jugado_minutos -> semi-aditiva  (engagement; no sumar
--                             entre periodos sin cuidado)
-- ------------------------------------------------------------
CREATE TABLE dw.hechos_ventas (
    venta_id        BIGSERIAL PRIMARY KEY,

    -- Claves foráneas hacia las dimensiones
    tiempo_id       INT NOT NULL REFERENCES dw.dim_tiempo(tiempo_id),
    juego_id        INT NOT NULL REFERENCES dw.dim_juego(juego_id),
    usuario_id      INT NOT NULL REFERENCES dw.dim_usuario(usuario_id),
    metodo_pago_id  INT          REFERENCES dw.dim_metodo_pago(metodo_pago_id),

    -- Medidas (los hechos numéricos del negocio)
    monto                  DECIMAL(10,2) NOT NULL,
    cantidad               INT           NOT NULL DEFAULT 1,
    tiempo_jugado_minutos  INT           DEFAULT 0
);


-- ------------------------------------------------------------
--  ÍNDICES sobre las claves foráneas.
--  Aceleran los JOIN entre hechos y dimensiones, que es la
--  operación más común en las consultas analíticas.
-- ------------------------------------------------------------
CREATE INDEX idx_hv_tiempo   ON dw.hechos_ventas(tiempo_id);
CREATE INDEX idx_hv_juego    ON dw.hechos_ventas(juego_id);
CREATE INDEX idx_hv_usuario  ON dw.hechos_ventas(usuario_id);
CREATE INDEX idx_hv_metodo   ON dw.hechos_ventas(metodo_pago_id);


-- ============================================================
--  Comprobación rápida después de poblar (vía ETL):
--
--  -- Ingresos por año (clásica consulta OLAP por dim_tiempo)
--  SELECT t.anio, SUM(h.monto) AS ingresos
--  FROM dw.hechos_ventas h
--  JOIN dw.dim_tiempo t ON h.tiempo_id = t.tiempo_id
--  GROUP BY t.anio
--  ORDER BY t.anio;
--
--  -- Ventas por categoría
--  SELECT j.categoria, COUNT(*) AS ventas, SUM(h.monto) AS ingresos
--  FROM dw.hechos_ventas h
--  JOIN dw.dim_juego j ON h.juego_id = j.juego_id
--  GROUP BY j.categoria
--  ORDER BY ingresos DESC;
-- ============================================================
