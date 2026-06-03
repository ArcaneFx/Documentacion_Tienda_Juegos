import sys
from database import get_db_connection
from auth import login_user, register_user
from datos_sinteticos import cargar_datos_sinteticos
import transacciones_crud as crud

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
        # Consulta parametrizada segura
        query = f"SELECT 1 FROM {tabla} WHERE {columna_id} = %s;"
        cur.execute(query, (valor_id,))
        existe = cur.fetchone() is not None
        return existe
    except Exception as e:
        print(f"Error de validación interna en la tabla '{tabla}': {e}")
        return False
    finally:
        cur.close()
        conn.close()


def menu_tienda(usuario_id):
    while True:
        print("\n--- 🎮 TIENDA DE JUEGOS ---")
        print("1. Añadir un juego al Carrito")
        print("2. Comprar un juego (Procesar Transacción Atómica)")
        print("3. Abonar saldo a la Cartera Virtual")
        print("4. Escribir una Reseña de un juego")
        print("0. Cerrar Sesión")
        
        opcion = input("Seleccione una acción: ").strip()
        
        if opcion == "1":
            juego_id = solicitar_id_valido("Ingrese el ID del juego que desea agregar: ")
            
            # Validación de existencia del juego
            if not verificar_existencia_registro("juegos", "juego_id", juego_id):
                print(f"Error: El juego con ID {juego_id} no existe en el catálogo.")
                continue
                
            # Si pasa la validación, llamamos de forma segura a su función
            exito, msg = crud.agregar_al_carrito(usuario_id, juego_id)
            print(f"\nResultado: {msg}")
            
        elif opcion == "2":
            juego_id = solicitar_id_valido("Ingrese el ID del juego que va a comprar: ")
            
            # Validaciones previas a la transacción
            if not verificar_existencia_registro("juegos", "juego_id", juego_id):
                print(f"Error: El juego con ID {juego_id} no existe en el catálogo.")
                continue
                
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT precio FROM juegos WHERE juego_id = %s;", (juego_id,))
            precio_juego = cur.fetchone()[0]
            cur.close()
            conn.close()
            
            # Ejecución limpia del CRUD transaccional
            exito, msg = crud.procesar_compra_juego(usuario_id, juego_id, precio_juego, usar_cartera=True)
            print(f"\n{msg}")
            
        elif opcion == "3":
            try:
                monto = float(input("Ingrese el monto a cargar: $").strip())
                if monto <= 0:
                    print("El monto debe ser un valor estrictamente mayor a cero.")
                    continue
            except ValueError:
                print("Formato incorrecto. Ingrese un valor numérico válido.")
                continue
                
            exito, msg = crud.cargar_saldo_cartera(usuario_id, monto)
            print(f"\nResultado: {msg}")
            
        elif opcion == "4":
            juego_id = solicitar_id_valido("Ingrese el ID del juego a reseñar: ")
            
            if not verificar_existencia_registro("juegos", "juego_id", juego_id):
                print(f"Error: El juego con ID {juego_id} no existe en la base de datos.")
                continue
                
            contenido = input("Escriba su reseña: ").strip()
            if not contenido:
                print("El contenido de la reseña no puede estar vacío.")
                continue
                
            recomienda_input = input("¿Recomienda este juego? (S/N): ").strip().upper()
            recomienda = recomienda_input == 'S'
            
            exito, msg = crud.publicar_resena(usuario_id, juego_id, contenido, recomienda)
            print(f"\nResultado: {msg}")
            
        elif opcion == "0":
            print("Cerrando sesión de usuario...")
            break
        else:
            print("Opción no válida.")

def menu_principal():
    while True:
        print("\n===== PLATAFORMA DE INGRESO =====")
        print("1. Iniciar Sesión (Login)")
        print("2. Registrar nuevo Usuario")
        print("0. Salir del Programa")
        
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            username = input("Nombre de usuario: ").strip()
            password = input("Contraseña: ").strip()
            
            if not username or not password:
                print("Los campos no pueden estar vacíos.")
                continue
                
            # Lógica de autenticación en auth.py
            usuario_id = login_user(username, password)
            
            if usuario_id:
                menu_tienda(usuario_id)
                
        elif opcion == "2":
            username = input("Cree un nombre de usuario: ").strip()
            correo = input("Ingrese su correo: ").strip()
            password = input("Cree su contraseña: ").strip()
            
            if not username or not correo or not password:
                print("Todos los campos son obligatorios para el registro.")
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
    cargar_datos_sinteticos() #carga los primeros 500 usuarios
    time.sleep(4) #espera 4 segundos
    cargar_datos_sinteticos() #carga los 3 usuarios particulares
    #si los 503 usuarios ya estan cargados, simplemente pasa de largo
    #TEST TEST TEST
    # usuarios particulares: 
    # nombre pass: contraseña
    # arkantosalmirante pass: almirantesenior
    # chuckmcgill pass: estadisticopesao
    # panxocloloco pass: panxoxo
    # TEST TEST TEST

    menu_principal()
