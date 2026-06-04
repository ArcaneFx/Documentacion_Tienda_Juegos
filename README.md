# Proyecto Final: Tienda de Videojuegos Desktop

## 1. Resumen del Proyecto

Este repositorio contiene el código fuente de nuestro proyecto final, una aplicación de escritorio para la simulación de una tienda de videojuegos. La aplicación fue desarrollada en Python utilizando la librería Tkinter para la interfaz gráfica y PostgreSQL como sistema de gestión de base de datos.

El objetivo principal fue aplicar los conocimientos de bases de datos y desarrollo de software para crear un sistema funcional que permita a los usuarios registrarse, explorar un catálogo de juegos, gestionar un carrito de compras y realizar transacciones.

## 2. Características Implementadas

El sistema cuenta con las siguientes funcionalidades clave:

*   **Autenticación de Usuarios:** Sistema de registro e inicio de sesión con hashing de contraseñas.
*   **Catálogo de Juegos:** Visualización de juegos con paginación y funcionalidad de búsqueda.
*   **Gestión de Perfil:** Los usuarios pueden ver su información y cargar saldo a su cartera virtual.
*   **Carrito de Compras:** Funcionalidad para agregar, eliminar y comprar juegos.
*   **Biblioteca Personal:** Los juegos comprados se añaden a una biblioteca personal.
*   **Sistema de Reseñas:** Posibilidad de escribir y publicar reseñas de los juegos adquiridos.
*   **Historial de Compras:** Registro de todas las transacciones realizadas por el usuario.

## 3. Guía de Instalación y Puesta en Marcha

Para poder ejecutar el proyecto en un entorno local, es necesario seguir los siguientes pasos.

### 3.1. Requisitos Previos

*   **Python:** Asegurarse de tener Python instalado (versión 3.8 o superior).
*   **PostgreSQL:** Se necesita una instancia de PostgreSQL activa.
*   **Git:** Para clonar este repositorio.

### 3.2. Pasos de Instalación

1.  **Clonar el Repositorio:**
    Abrir una terminal y ejecutar el siguiente comando para descargar los archivos del proyecto.
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd Documentacion_Tienda_Juegos
    ```

2.  **Instalar Dependencias de Python:**
    El archivo `requirements.txt` contiene todas las librerías que necesita el programa. Para instalarlas, usar el gestor de paquetes `pip`.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar la Base de Datos:**
    *   Ejecutar el script `create-bd.sql` en tu gestor de PostgreSQL (como pgAdmin) para crear todas las tablas necesarias.
    *   **Importante:** Modificar el archivo `database.py` con tus credenciales de conexión a la base de datos (usuario, contraseña, host y nombre de la base de datos).

    ```python
    # proyectof/database.py
    def get_db_connection():
        # ...
        connection = psycopg2.connect(
            host="TU_HOST",
            database="TU_BASE_DE_DATOS",
            user="TU_USUARIO",
            password="TU_CONTRASEÑA"
        )
        # ...
    ```

4.  **Poblar la Base de Datos (Opcional):**
    Para tener datos de prueba, se pueden ejecutar los scripts `datos_sinteticos.sql` o correr el archivo `datos_sinteticos.py`.

## 4. Ejecución de la Aplicación

Una vez completada la instalación, la aplicación se puede iniciar ejecutando el archivo `main.py` que se encuentra en la carpeta `proyectof`.

```bash
python proyectof/main.py
```
Esto lanzará la interfaz gráfica de la tienda.

## 5. Equipo de Desarrollo

*   Francisco Rivera
*   Hans Benicke
*   Jason Cardenas
*   Benjamin Parra
*   Sebastian Rubilar


