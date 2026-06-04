CREATE TABLE usuarios (
    usuario_id SERIAL PRIMARY KEY,
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
    correo_electronico VARCHAR(100) UNIQUE NOT NULL,
    contrasena_hash VARCHAR(255) NOT NULL,
    saldo_cartera DECIMAL(10, 2) DEFAULT 0.00,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE juegos (
    juego_id SERIAL PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10, 2) NOT NULL,
    fecha_lanzamiento DATE,
    desarrollador VARCHAR(100),
    editor VARCHAR(100)
);

CREATE TABLE categorias (
    categoria_id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL -- 'Indie', 'Acción', 'Estrategia'
);

CREATE TABLE juegos_categorias (
    juego_id INT REFERENCES juegos(juego_id) ON DELETE CASCADE,
    categoria_id INT REFERENCES categorias(categoria_id) ON DELETE CASCADE,
    PRIMARY KEY (juego_id, categoria_id)
);


CREATE TABLE lista_deseos (
    usuario_id INT REFERENCES usuarios(usuario_id) ON DELETE CASCADE,
    juego_id INT REFERENCES juegos(juego_id) ON DELETE CASCADE,
    fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (usuario_id, juego_id)
);

CREATE TABLE carrito_compras (
    carrito_item_id SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(usuario_id) ON DELETE CASCADE,
    juego_id INT REFERENCES juegos(juego_id) ON DELETE CASCADE,
    fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(usuario_id, juego_id)
);


CREATE TABLE metodos_pago (
    metodo_pago_id SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(usuario_id) ON DELETE CASCADE,
    proveedor VARCHAR(20) NOT NULL, -- 'Visa', 'PayPal', 'Cartera Steam'
    ultimos_cuatro_digitos VARCHAR(4),
    es_predeterminado BOOLEAN DEFAULT FALSE
);

CREATE TABLE transacciones (
    transaccion_id SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(usuario_id),
    metodo_pago_id INT REFERENCES metodos_pago(metodo_pago_id),
    monto_total DECIMAL(10, 2) NOT NULL,
    estado VARCHAR(20) DEFAULT 'completado', -- 'pendiente', 'fallido', 'reembolsado'
    fecha_transaccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE biblioteca (
    usuario_id INT REFERENCES usuarios(usuario_id) ON DELETE CASCADE,
    juego_id INT REFERENCES juegos(juego_id) ON DELETE CASCADE,
    fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tiempo_jugado_minutos INT DEFAULT 0,
    ultima_vez_jugado TIMESTAMP,
    PRIMARY KEY (usuario_id, juego_id)
);


CREATE TABLE logros (
    logro_id SERIAL PRIMARY KEY,
    juego_id INT REFERENCES juegos(juego_id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    url_icono VARCHAR(255),
    es_oculto BOOLEAN DEFAULT FALSE
);

CREATE TABLE logros_usuarios (
    usuario_id INT REFERENCES usuarios(usuario_id) ON DELETE CASCADE,
    logro_id INT REFERENCES logros(logro_id) ON DELETE CASCADE,
    fecha_desbloqueo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (usuario_id, logro_id)
);


CREATE TABLE resenas (
    resena_id SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(usuario_id),
    juego_id INT REFERENCES juegos(juego_id),
    contenido TEXT,
    recomendado BOOLEAN DEFAULT TRUE,
    fecha_publicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);