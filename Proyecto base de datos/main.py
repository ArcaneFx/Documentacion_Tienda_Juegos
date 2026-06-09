# main.py
# Integrante: Jason
# Punto de entrada del programa. Maneja validaciones de input y conecta
# todos los módulos: auth, consultas y transacciones_crud.

import sys
from database import get_db_connection
from auth import login_user, register_user
import transacciones_crud as crud
import consultas as q


# ══════════════════════════════════════════════
#  HELPERS DE VALIDACIÓN
# ══════════════════════════════════════════════

def solicitar_id_valido(mensaje):
    """Asegura que el usuario ingrese un número entero positivo."""
    while True:
        entrada = input(mensaje).strip()
        if entrada.isdigit() and int(entrada) > 0:
            return int(entrada)
        print("Entrada inválida. Debe ingresar un número entero positivo.")


def verificar_existencia_registro(tabla, columna_id, valor_id):
    """Comprueba si un ID existe físicamente en una tabla específica."""
    conn = get_db_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        query = f"SELECT 1 FROM {tabla} WHERE {columna_id} = %s;"
        cur.execute(query, (valor_id,))
        return cur.fetchone() is not None
    except Exception as e:
        print(f"Error de validación interna en la tabla '{tabla}': {e}")
        return False
    finally:
        cur.close()
        conn.close()


def obtener_precio_juego(juego_id):
    """Obtiene el precio de un juego de forma segura."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT precio FROM juegos WHERE juego_id = %s;", (juego_id,))
        resultado = cur.fetchone()
        return resultado[0] if resultado else None
    except Exception as e:
        print(f"Error al obtener precio: {e}")
        return None
    finally:
        cur.close()
        conn.close()


# ══════════════════════════════════════════════
#  MENÚ DE CONSULTAS (Hans)
# ══════════════════════════════════════════════

def menu_consultas(usuario_id):
    while True:
        print("\n--- 🔍 CONSULTAS ---")
        print("1. Ver catálogo completo de juegos")
        print("2. Buscar juego por nombre")
        print("3. Ver juegos por categoría")
        print("4. Ver juegos por rango de precio")
        print("5. Ver mi biblioteca")
        print("6. Ver mi perfil")
        print("7. Ver mis logros")
        print("8. Ver mi carrito")
        print("9. Ver mi historial de compras")
        print("10. Ver reseñas de un juego")
        print("11. Ver calificaciones de un juego")
        print("12. Top juegos más vendidos (feed tienda)")
        print("13. Ranking juegos mejor calificados")
        print("0. Volver")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            q.listar_juegos()

        elif opcion == "2":
            texto = input("Ingrese el nombre a buscar: ").strip()
            if not texto:
                print("El texto no puede estar vacío.")
                continue
            q.buscar_juego_por_nombre(texto)

        elif opcion == "3":
            print("Categorías disponibles: Acción, RPG, Indie, Estrategia, Terror, Deportes, Simulación, Aventura")
            categoria = input("Ingrese la categoría: ").strip()
            if not categoria:
                print("Debe ingresar una categoría.")
                continue
            print("Ordenar por: 1) Ventas  2) Precio menor  3) Precio mayor  4) Aprobación")
            orden_op = input("Opción (Enter para ventas): ").strip()
            ordenes = {"1": "ventas", "2": "precio_asc", "3": "precio_desc", "4": "aprobacion"}
            orden = ordenes.get(orden_op, "ventas")
            q.listar_juegos_por_categoria(categoria, orden)

        elif opcion == "4":
            try:
                precio_min = float(input("Precio mínimo: $").strip())
                precio_max = float(input("Precio máximo: $").strip())
                if precio_min < 0 or precio_max < precio_min:
                    print("Rango de precios inválido.")
                    continue
            except ValueError:
                print("Ingrese valores numéricos válidos.")
                continue
            q.listar_juegos_por_precio(precio_min, precio_max)

        elif opcion == "5":
            q.mostrar_biblioteca(usuario_id)

        elif opcion == "6":
            q.mostrar_perfil_usuario(usuario_id)

        elif opcion == "7":
            q.mostrar_logros_usuario(usuario_id)

        elif opcion == "8":
            q.mostrar_carrito(usuario_id)

        elif opcion == "9":
            q.mostrar_historial_compras(usuario_id)

        elif opcion == "10":
            juego_id = solicitar_id_valido("Ingrese el ID del juego: ")
            if not verificar_existencia_registro("juegos", "juego_id", juego_id):
                print(f"Error: El juego con ID {juego_id} no existe.")
                continue
            q.mostrar_resenas_juego(juego_id)

        elif opcion == "11":
            juego_id = solicitar_id_valido("Ingrese el ID del juego: ")
            if not verificar_existencia_registro("juegos", "juego_id", juego_id):
                print(f"Error: El juego con ID {juego_id} no existe.")
                continue
            q.promedio_calificaciones_juego(juego_id)

        elif opcion == "12":
            q.feed_juegos_mas_vendidos(limite=10)

        elif opcion == "13":
            try:
                minimo = int(input("Mínimo de reseñas requeridas (Enter para 5): ").strip() or "5")
            except ValueError:
                minimo = 5
            q.ranking_juegos_mejor_calificados(minimo_resenas=minimo, limite=10)

        elif opcion == "0":
            break
        else:
            print("Opción no válida.")


# ══════════════════════════════════════════════
#  MENÚ DE TIENDA (transacciones)
# ══════════════════════════════════════════════

def menu_tienda(usuario_id):
    while True:
        print("\n--- 🎮 TIENDA DE JUEGOS ---")
        print("1. Añadir un juego al carrito")
        print("2. Comprar un juego (transacción)")
        print("3. Abonar saldo a la cartera virtual")
        print("4. Escribir una reseña de un juego")
        print("0. Cerrar sesión")

        opcion = input("Seleccione una acción: ").strip()

        if opcion == "1":
            # Mostrar catálogo para que el usuario sepa qué IDs existen
            ver = input("¿Desea ver el catálogo primero? (S/N): ").strip().upper()
            if ver == "S":
                q.listar_juegos()

            juego_id = solicitar_id_valido("Ingrese el ID del juego que desea agregar: ")
            if not verificar_existencia_registro("juegos", "juego_id", juego_id):
                print(f"Error: El juego con ID {juego_id} no existe en el catálogo.")
                continue

            exito, msg = crud.agregar_al_carrito(usuario_id, juego_id)
            print(f"\nResultado: {msg}")

        elif opcion == "2":
            # Mostrar carrito antes de comprar
            ver = input("¿Desea ver su carrito primero? (S/N): ").strip().upper()
            if ver == "S":
                q.mostrar_carrito(usuario_id)

            juego_id = solicitar_id_valido("Ingrese el ID del juego que va a comprar: ")
            if not verificar_existencia_registro("juegos", "juego_id", juego_id):
                print(f"Error: El juego con ID {juego_id} no existe en el catálogo.")
                continue

            precio = obtener_precio_juego(juego_id)
            if precio is None:
                print("No se pudo obtener el precio del juego.")
                continue

            print(f"Precio del juego: ${precio:.2f}")
            usar_cartera = input("¿Usar saldo de cartera? (S/N): ").strip().upper() == "S"

            exito, msg = crud.procesar_compra_juego(usuario_id, juego_id, precio, usar_cartera)
            print(f"\n{msg}")

        elif opcion == "3":
            try:
                monto = float(input("Ingrese el monto a cargar: $").strip())
                if monto <= 0:
                    print("El monto debe ser mayor a cero.")
                    continue
            except ValueError:
                print("Formato incorrecto. Ingrese un valor numérico válido.")
                continue

            exito, msg = crud.cargar_saldo_cartera(usuario_id, monto)
            print(f"\nResultado: {msg}")

        elif opcion == "4":
            # Mostrar biblioteca para que sepa qué juegos puede reseñar
            ver = input("¿Desea ver su biblioteca primero? (S/N): ").strip().upper()
            if ver == "S":
                q.mostrar_biblioteca(usuario_id)

            juego_id = solicitar_id_valido("Ingrese el ID del juego a reseñar: ")
            if not verificar_existencia_registro("juegos", "juego_id", juego_id):
                print(f"Error: El juego con ID {juego_id} no existe.")
                continue

            contenido = input("Escriba su reseña: ").strip()
            if not contenido:
                print("La reseña no puede estar vacía.")
                continue

            recomienda = input("¿Recomienda este juego? (S/N): ").strip().upper() == "S"
            exito, msg = crud.publicar_resena(usuario_id, juego_id, contenido, recomienda)
            print(f"\nResultado: {msg}")

        elif opcion == "0":
            print("Cerrando sesión...")
            break
        else:
            print("Opción no válida.")


# ══════════════════════════════════════════════
#  MENÚ PRINCIPAL
# ══════════════════════════════════════════════

def menu_usuario(usuario_id):
    """Menú principal después de hacer login."""
    while True:
        print("\n===== MENÚ PRINCIPAL =====")
        print("1. 🎮 Tienda (comprar, carrito, reseñas)")
        print("2. 🔍 Consultas (buscar juegos, ver biblioteca, etc.)")
        print("0. Cerrar sesión")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            menu_tienda(usuario_id)
        elif opcion == "2":
            menu_consultas(usuario_id)
        elif opcion == "0":
            print("Cerrando sesión...")
            break
        else:
            print("Opción no válida.")


def menu_principal():
    while True:
        print("\n===== PLATAFORMA DE INGRESO =====")
        print("1. Iniciar sesión")
        print("2. Registrar nuevo usuario")
        print("0. Salir del programa")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            username = input("Nombre de usuario: ").strip()
            password = input("Contraseña: ").strip()

            if not username or not password:
                print("Los campos no pueden estar vacíos.")
                continue

            usuario_id = login_user(username, password)
            if usuario_id:
                menu_usuario(usuario_id)

        elif opcion == "2":
            username = input("Cree un nombre de usuario: ").strip()
            correo   = input("Ingrese su correo: ").strip()
            password = input("Cree su contraseña: ").strip()

            if not username or not correo or not password:
                print("Todos los campos son obligatorios.")
                continue
            if "@" not in correo:
                print("Formato de correo electrónico no válido.")
                continue

            register_user(username, correo, password)

        elif opcion == "0":
            print("Apagando el sistema. ¡Adiós!")
            sys.exit()
        else:
            print("Opción incorrecta.")


if __name__ == "__main__":
    menu_principal()
