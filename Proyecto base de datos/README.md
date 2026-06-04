# 🎮 Tienda de Videojuegos — Sistema Transaccional

Proyecto de Base de Datos (INFO147) — Entrega 2

Sistema transaccional para una tienda de videojuegos estilo Steam, desarrollado en
Python con PostgreSQL. Permite registrar usuarios, explorar un catálogo de juegos,
agregarlos al carrito, comprarlos (transacción que afecta varias tablas), gestionar
una biblioteca personal, escribir reseñas y desbloquear logros.

## 👥 Integrantes

- **Ruby** — Conexión a la base de datos y carga de datos sintéticos
- **Parra** — Funciones que ingresan y eliminan datos (CRUD)
- **Hans** — Funciones de consulta (listados, reportes con SELECT y JOIN)
- **Jason** — Lógica principal y validaciones de entrada
- **Francisco** — Interfaz gráfica

## 📋 Requisitos

- Python 3
- PostgreSQL
- Las librerías de `requirements.txt`

## ⚙️ Instalación

1. Instalar las librerías de Python:

```
pip install -r requirements.txt
```

2. Crear la base de datos en PostgreSQL (por ejemplo con DBeaver), con el nombre `test3`.

3. Configurar la contraseña en `database.py` con la de tu PostgreSQL local:

```python
connection = psycopg2.connect(
    host="localhost",
    database="test3",
    user="postgres",
    password="TU_CONTRASEÑA"
)
```

## 🚀 Cómo ejecutar

Seguir este orden:

**1. Crear las tablas** — ejecutar `create-bd.sql` en DBeaver.

**2. Cargar los datos sintéticos** — ejecutar dos veces:

```
python datos_sinteticos.py
```

- La 1ª vez carga los 40.000 datos sintéticos (4 años de actividad).
- La 2ª vez carga los 3 usuarios de demostración.

**3. Iniciar el programa** (interfaz gráfica):

```
python interfaz.py
```

## 🔑 Usuarios de demostración

Para probar el login durante la presentación:

| Usuario              | Contraseña         | Saldo    |
|----------------------|--------------------|----------|
| arkantosalmirante    | almirantesenior    | $0.00    |
| panxocloloco         | panxoxo            | $25.50   |
| chuckmcgill          | estadisticopesao   | $500.00  |

## 📂 Estructura del proyecto

```
├── database.py                    # Conexión a PostgreSQL
├── auth.py                        # Login y registro (bcrypt)
├── datos_sinteticos.py            # Carga los datos
├── transacciones_crud.py          # Ingresar y eliminar datos
├── consultas.py                   # Consultas / listados (SELECT, JOIN)
├── consultas_extra.py             # Consultas adicionales / reportes
├── interfaz.py                    # Interfaz gráfica (programa principal)
├── main.py                        # Versión por consola (alternativa)
├── create-bd.sql                  # Esquema de la base de datos
├── datos_sinteticos.sql           # 40.000 registros sintéticos
├── datos_sinteticos_de_prueba.sql # Usuarios de demostración
├── requirements.txt               # Librerías necesarias
└── diccionario_datos.xlsx         # Diccionario de datos
```
