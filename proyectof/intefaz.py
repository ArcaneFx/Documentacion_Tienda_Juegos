import tkinter as tk
from tkinter import ttk, messagebox

from consultas import (
    listar_juegos,
    contar_juegos,
    buscar_juego_por_nombre,
    mostrar_perfil_usuario,
    mostrar_biblioteca,
    mostrar_carrito,
    mostrar_historial_compras,
    feed_juegos_mas_vendidos
)
from transacciones_crud import (
    registrar_usuario,
    agregar_al_carrito,
    eliminar_juego_carrito,
    procesar_compra_juego,
    cargar_saldo_cartera,
    publicar_resena
)
from auth import login_user, register_user

# usuario logueado actualmente
usuario_activo = {"id": None, "nombre": None}


# ══════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════

def crear_tabla(parent, columnas):
    frame = tk.Frame(parent)
    frame.pack(fill="both", expand=True, padx=10, pady=5)

    scroll = ttk.Scrollbar(frame, orient="vertical")
    tabla = ttk.Treeview(frame, columns=columnas, show="headings",
                         yscrollcommand=scroll.set)
    scroll.config(command=tabla.yview)

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=130, anchor="center")

    tabla.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    return tabla


def llenar_tabla(tabla, datos):
    for fila in tabla.get_children():
        tabla.delete(fila)
    if datos:
        for fila in datos:
            tabla.insert("", "end", values=fila)


# ══════════════════════════════════════════════
#  LOGIN Y REGISTRO
# ══════════════════════════════════════════════

def ventana_login():
    win = tk.Toplevel()
    win.title("Iniciar sesión")
    win.geometry("350x280")
    win.grab_set()

    tk.Label(win, text="Iniciar sesión", font=("Arial", 13, "bold")).pack(pady=15)

    tk.Label(win, text="Usuario:").pack()
    entry_user = tk.Entry(win, width=30)
    entry_user.pack(pady=4)

    tk.Label(win, text="Contraseña:").pack()
    entry_pass = tk.Entry(win, width=30, show="*")
    entry_pass.pack(pady=4)

    lbl_error = tk.Label(win, text="", fg="red")
    lbl_error.pack()

    def hacer_login():
        nombre = entry_user.get().strip()
        passwd = entry_pass.get().strip()
        if not nombre or not passwd:
            lbl_error.config(text="Completa todos los campos.")
            return
        uid = login_user(nombre, passwd)
        if uid:
            usuario_activo["id"]     = uid
            usuario_activo["nombre"] = nombre
            win.destroy()
            if lbl_bienvenida_ref:
                lbl_bienvenida_ref.config(text=f"Bienvenido, {nombre}")
            if btn_login_ref:
                btn_login_ref.config(text="Cerrar sesión", command=cerrar_sesion)
        else:
            lbl_error.config(text="Usuario o contraseña incorrectos.")

    def abrir_registro():
        win.destroy()
        ventana_registro()

    tk.Button(win, text="Entrar", command=hacer_login, width=20).pack(pady=8)
    tk.Button(win, text="¿No tienes cuenta? Regístrate",
              command=abrir_registro, relief="flat", fg="blue").pack()


def ventana_registro():
    win = tk.Toplevel()
    win.title("Registrarse")
    win.geometry("350x300")
    win.grab_set()

    tk.Label(win, text="Crear cuenta", font=("Arial", 13, "bold")).pack(pady=15)

    tk.Label(win, text="Nombre de usuario:").pack()
    entry_user = tk.Entry(win, width=30)
    entry_user.pack(pady=4)

    tk.Label(win, text="Correo:").pack()
    entry_correo = tk.Entry(win, width=30)
    entry_correo.pack(pady=4)

    tk.Label(win, text="Contraseña:").pack()
    entry_pass = tk.Entry(win, width=30, show="*")
    entry_pass.pack(pady=4)

    lbl_error = tk.Label(win, text="", fg="red")
    lbl_error.pack()

    def hacer_registro():
        nombre = entry_user.get().strip()
        correo = entry_correo.get().strip()
        passwd = entry_pass.get().strip()
        if not all([nombre, correo, passwd]):
            lbl_error.config(text="Completa todos los campos.")
            return
        if "@" not in correo:
            lbl_error.config(text="Correo no válido.")
            return
        register_user(nombre, correo, passwd)
        messagebox.showinfo("Éxito", "Cuenta creada. Ahora inicia sesión.")
        win.destroy()
        ventana_login()

    tk.Button(win, text="Registrarse", command=hacer_registro, width=20).pack(pady=10)
    tk.Button(win, text="Volver",
              command=lambda: [win.destroy(), ventana_login()],
              relief="flat", fg="blue").pack()


# ══════════════════════════════════════════════
#  CATÁLOGO — ver juegos y agregar al carrito
# ══════════════════════════════════════════════

def ventana_catalogo():
    win = tk.Toplevel()
    win.title("Juegos")
    win.geometry("800x520")

    tk.Label(win, text="Catálogo de juegos", font=("Arial", 12, "bold")).pack(pady=8)

    # barra de búsqueda
    frame_busq = tk.Frame(win)
    frame_busq.pack(fill="x", padx=10)

    tk.Label(frame_busq, text="Buscar:").pack(side="left")
    entry_busq = tk.Entry(frame_busq, width=30)
    entry_busq.pack(side="left", padx=5)

    # estado de paginación
    # estado de paginación — solo guarda página actual, total y filtro
    POR_PAGINA = 10
    estado = {"pagina": 0, "total": 0, "filtro": ""}

    columnas = ("ID", "Título", "Categoría", "Precio", "Desarrollador")
    tabla = crear_tabla(win, columnas)
    tabla.column("ID",            width=40)
    tabla.column("Título",        width=200)
    tabla.column("Categoría",     width=100)
    tabla.column("Precio",        width=70)
    tabla.column("Desarrollador", width=160)

    lbl_pagina = tk.Label(win, text="")
    lbl_pagina.pack()

    # botones creados ANTES de mostrar_pagina
    frame_pag = tk.Frame(win)
    frame_pag.pack(pady=4)

    btn_anterior  = tk.Button(frame_pag, text="← Anterior", width=12, state="disabled")
    btn_anterior.grid(row=0, column=0, padx=10)

    btn_siguiente = tk.Button(frame_pag, text="Siguiente →", width=12)
    btn_siguiente.grid(row=0, column=1, padx=10)

    def mostrar_pagina():
        offset = estado["pagina"] * POR_PAGINA
        if estado["filtro"]:
            # búsqueda: trae todo y pagina en memoria (pocos resultados)
            todos = buscar_juego_por_nombre(estado["filtro"])
            llenar_tabla(tabla, todos[offset:offset + POR_PAGINA])
            estado["total"] = len(todos)
        else:
            # sin filtro: solo trae 10 desde la BD con LIMIT/OFFSET
            llenar_tabla(tabla, listar_juegos(limite=POR_PAGINA, offset=offset))
            estado["total"] = contar_juegos()

        total_pag = max(1, -(-estado["total"] // POR_PAGINA))
        lbl_pagina.config(
            text=f"Página {estado['pagina']+1} de {total_pag}  ({estado['total']} juegos)")
        btn_anterior.config(state="normal" if estado["pagina"] > 0 else "disabled")
        hay_sig = (estado["pagina"] + 1) * POR_PAGINA < estado["total"]
        btn_siguiente.config(state="normal" if hay_sig else "disabled")

    def pagina_anterior():
        estado["pagina"] -= 1
        mostrar_pagina()

    def pagina_siguiente():
        estado["pagina"] += 1
        mostrar_pagina()

    btn_anterior.config(command=pagina_anterior)
    btn_siguiente.config(command=pagina_siguiente)

    def cargar(filtro=""):
        estado["pagina"] = 0
        estado["filtro"] = filtro
        mostrar_pagina()

    cargar()

    tk.Button(frame_busq, text="Buscar",
              command=lambda: cargar(entry_busq.get().strip())).pack(side="left", padx=4)
    tk.Button(frame_busq, text="Ver todos",
              command=lambda: [entry_busq.delete(0, "end"), cargar()]).pack(side="left")

    # panel inferior
    frame_inf = tk.Frame(win, relief="groove", bd=1)
    frame_inf.pack(fill="x", padx=10, pady=8)

    lbl_sel = tk.Label(frame_inf, text="Selecciona un juego")
    lbl_sel.pack(side="left", padx=15, pady=8)

    def al_seleccionar(event):
        try:
            vals = tabla.item(tabla.selection()[0], "values")
            lbl_sel.config(text=f"{vals[1]}  |  {vals[2]}  |  ${vals[3]}")
        except IndexError:
            pass

    tabla.bind("<<TreeviewSelect>>", al_seleccionar)

    def agregar():
        if not usuario_activo["id"]:
            messagebox.showwarning("Aviso", "Debes iniciar sesión primero.")
            return
        try:
            vals     = tabla.item(tabla.selection()[0], "values")
            juego_id = int(vals[0])
            titulo   = vals[1]
        except IndexError:
            messagebox.showwarning("Aviso", "Selecciona un juego primero.")
            return
        exito, msg = agregar_al_carrito(usuario_activo["id"], juego_id)
        if exito:
            messagebox.showinfo("Éxito", f"'{titulo}' agregado al carrito.")
        else:
            messagebox.showerror("Error", msg)

    tk.Button(frame_inf, text="Agregar al carrito",
              command=agregar, width=20).pack(side="right", padx=15, pady=8)


# ══════════════════════════════════════════════
#  MI PERFIL
# ══════════════════════════════════════════════

def ventana_perfil():
    if not usuario_activo["id"]:
        messagebox.showwarning("Aviso", "Debes iniciar sesión primero.")
        return

    win = tk.Toplevel()
    win.title("Mi perfil")
    win.geometry("380x320")

    perfil = mostrar_perfil_usuario(usuario_activo["id"])
    if not perfil:
        messagebox.showerror("Error", "No se pudo cargar el perfil.")
        win.destroy()
        return

    uid, nombre, correo, saldo, fecha_reg, juegos, logros = perfil

    tk.Label(win, text="Mi perfil", font=("Arial", 13, "bold")).pack(pady=15)

    for etiqueta, valor in [
        ("ID",           uid),
        ("Usuario",      nombre),
        ("Correo",       correo),
        ("Saldo",        f"${saldo:.2f}"),
        ("Registro",     fecha_reg.strftime('%d/%m/%Y')),
        ("Juegos",       juegos),
    ]:
        f = tk.Frame(win)
        f.pack(fill="x", padx=30, pady=2)
        tk.Label(f, text=f"{etiqueta}:", width=12, anchor="w",
                 font=("Arial", 10, "bold")).pack(side="left")
        tk.Label(f, text=str(valor), anchor="w").pack(side="left")

    def cargar_saldo():
        win2 = tk.Toplevel()
        win2.title("Cargar saldo")
        win2.geometry("280x160")
        tk.Label(win2, text="Monto a cargar ($):").pack(pady=15)
        entry = tk.Entry(win2, width=15)
        entry.pack()

        def confirmar():
            try:
                monto = float(entry.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Ingresa un número válido.")
                return
            exito, msg = cargar_saldo_cartera(usuario_activo["id"], monto)
            messagebox.showinfo("Resultado", msg)
            win2.destroy()

        tk.Button(win2, text="Cargar", command=confirmar, width=15).pack(pady=10)

    tk.Button(win, text="Cargar saldo", command=cargar_saldo, width=20).pack(pady=12)


# ══════════════════════════════════════════════
#  BIBLIOTECA + RESEÑA
# ══════════════════════════════════════════════

def ventana_biblioteca():
    if not usuario_activo["id"]:
        messagebox.showwarning("Aviso", "Debes iniciar sesión primero.")
        return

    win = tk.Toplevel()
    win.title("Mi biblioteca")
    win.geometry("750x500")

    tk.Label(win, text="Mi biblioteca", font=("Arial", 12, "bold")).pack(pady=8)

    columnas = ("ID Juego", "Título", "Categoría", "Fecha compra", "Horas jugadas")
    tabla = crear_tabla(win, columnas)

    datos = mostrar_biblioteca(usuario_activo["id"])
    if datos:
        llenar_tabla(tabla, [
            (r[0], r[1], r[2], r[3].strftime('%d/%m/%Y'), f"{r[4]//60}h")
            for r in datos
        ])

    # panel inferior — escribir reseña del juego seleccionado
    frame_inf = tk.Frame(win, relief="groove", bd=1)
    frame_inf.pack(fill="x", padx=10, pady=8)

    tk.Label(frame_inf, text="Reseña del juego seleccionado:").pack(anchor="w", padx=10, pady=4)

    entry_resena = tk.Text(frame_inf, width=60, height=3)
    entry_resena.pack(padx=10, pady=4)

    recomienda = tk.BooleanVar(value=True)
    tk.Checkbutton(frame_inf, text="Recomiendo este juego",
                   variable=recomienda).pack(anchor="w", padx=10)

    def publicar():
        try:
            vals     = tabla.item(tabla.selection()[0], "values")
            juego_id = int(vals[0])
            titulo   = vals[1]
        except IndexError:
            messagebox.showwarning("Aviso", "Selecciona un juego de tu biblioteca.")
            return

        texto = entry_resena.get("1.0", "end").strip()
        if not texto:
            messagebox.showwarning("Aviso", "Escribe una reseña antes de publicar.")
            return

        exito, msg = publicar_resena(usuario_activo["id"], juego_id, texto, recomienda.get())
        if exito:
            messagebox.showinfo("Éxito", msg)
            entry_resena.delete("1.0", "end")
        else:
            messagebox.showerror("Error", msg)

    tk.Button(frame_inf, text="Publicar reseña",
              command=publicar, width=20).pack(pady=6)


# ══════════════════════════════════════════════
#  CARRITO
# ══════════════════════════════════════════════

def ventana_carrito():
    if not usuario_activo["id"]:
        messagebox.showwarning("Aviso", "Debes iniciar sesión primero.")
        return

    win = tk.Toplevel()
    win.title("Mi carrito")
    win.geometry("650x480")

    tk.Label(win, text="Mi carrito", font=("Arial", 12, "bold")).pack(pady=8)

    columnas = ("ID Juego", "Título", "Precio", "Fecha agregado")
    tabla = crear_tabla(win, columnas)

    datos = mostrar_carrito(usuario_activo["id"])
    total = 0
    if datos:
        for r in datos:
            tabla.insert("", "end", values=(r[0], r[1], f"${r[2]:.2f}",
                                            r[3].strftime('%d/%m/%Y')))
            total += r[2]

    lbl_total = tk.Label(win, text=f"Total: ${total:.2f}",
                         font=("Arial", 11, "bold"))
    lbl_total.pack(pady=4)

    frame_btns = tk.Frame(win)
    frame_btns.pack(pady=8)

    def eliminar():
        try:
            vals     = tabla.item(tabla.selection()[0], "values")
            juego_id = int(vals[0])
            titulo   = vals[1]
        except IndexError:
            messagebox.showwarning("Aviso", "Selecciona un juego para eliminar.")
            return
        ok = messagebox.askyesno("Confirmar", f"¿Eliminar '{titulo}' del carrito?")
        if ok:
            exito, msg = eliminar_juego_carrito(usuario_activo["id"], juego_id)
            messagebox.showinfo("Resultado", msg)
            win.destroy()
            ventana_carrito()

    def comprar_seleccionado():
        try:
            vals     = tabla.item(tabla.selection()[0], "values")
            juego_id = int(vals[0])
            titulo   = vals[1]
            precio   = float(vals[2].replace("$", ""))
        except IndexError:
            messagebox.showwarning("Aviso", "Selecciona un juego para comprar.")
            return
        ok = messagebox.askyesno("Confirmar", f"¿Comprar '{titulo}' por ${precio:.2f}?")
        if ok:
            exito, msg = procesar_compra_juego(
                usuario_activo["id"], juego_id, precio, usar_cartera=True)
            messagebox.showinfo("Resultado", msg)
            win.destroy()
            ventana_carrito()

    def comprar_todo():
        if not datos:
            messagebox.showwarning("Aviso", "El carrito está vacío.")
            return
        ok = messagebox.askyesno("Confirmar",
                                 f"¿Comprar todos los juegos por ${total:.2f}?")
        if ok:
            errores = []
            for r in datos:
                exito, msg = procesar_compra_juego(
                    usuario_activo["id"], r[0], r[2], usar_cartera=True)
                if not exito:
                    errores.append(r[1])
            if errores:
                messagebox.showwarning("Aviso",
                    f"Algunos juegos no pudieron comprarse: {', '.join(errores)}")
            else:
                messagebox.showinfo("Éxito", "¡Todos los juegos comprados!")
            win.destroy()
            ventana_carrito()

    tk.Button(frame_btns, text="Eliminar seleccionado",
              command=eliminar, width=20).grid(row=0, column=0, padx=8)
    tk.Button(frame_btns, text="Comprar seleccionado",
              command=comprar_seleccionado, width=20).grid(row=0, column=1, padx=8)
    tk.Button(frame_btns, text="Comprar todo el carrito",
              command=comprar_todo, width=20).grid(row=1, column=0, columnspan=2, pady=8)


# ══════════════════════════════════════════════
#  HISTORIAL
# ══════════════════════════════════════════════

def ventana_historial():
    if not usuario_activo["id"]:
        messagebox.showwarning("Aviso", "Debes iniciar sesión primero.")
        return

    win = tk.Toplevel()
    win.title("Historial de compras")
    win.geometry("700x420")

    tk.Label(win, text="Historial de compras", font=("Arial", 12, "bold")).pack(pady=8)

    columnas = ("# Boleta", "Monto", "Estado", "Método", "Fecha")
    tabla = crear_tabla(win, columnas)

    datos = mostrar_historial_compras(usuario_activo["id"])
    if datos:
        llenar_tabla(tabla, [
            (r[0], f"${r[1]:.2f}", r[2], r[4], r[3].strftime('%d/%m/%Y'))
            for r in datos
        ])


# ══════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════

# Variables globales para acceder a widgets desde otras funciones
lbl_bienvenida_ref = None
btn_login_ref = None


def cerrar_sesion():
    usuario_activo["id"]     = None
    usuario_activo["nombre"] = None
    if lbl_bienvenida_ref:
        lbl_bienvenida_ref.config(text="")
    if btn_login_ref:
        btn_login_ref.config(text="Iniciar sesión", command=ventana_login)
    messagebox.showinfo("Sesión", "Sesión cerrada.")


# ══════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ══════════════════════════════════════════════
def iniciar_aplicacion_gui():
    root = tk.Tk()
    root.title("Tienda de Videojuegos")
    root.geometry("400x420")
    root.resizable(False, False)

    tk.Label(root, text="Tienda de Videojuegos",
             font=("Arial", 15, "bold")).pack(pady=15)

    lbl_bienvenida = tk.Label(root, text="", font=("Arial", 10))
    lbl_bienvenida.pack()

    frame = tk.Frame(root)
    frame.pack(pady=10)

    btn_login = tk.Button(frame, text="Iniciar sesión", command=ventana_login, width=18)
    btn_login.grid(row=0, column=0, padx=8, pady=6)

    tk.Button(frame, text="Mi perfil",    command=ventana_perfil,    width=18)\
        .grid(row=0, column=1, padx=8, pady=6)
    tk.Button(frame, text="Ver juegos",   command=ventana_catalogo,  width=18)\
        .grid(row=1, column=0, padx=8, pady=6)
    tk.Button(frame, text="Mi biblioteca",command=ventana_biblioteca,width=18)\
        .grid(row=1, column=1, padx=8, pady=6)
    tk.Button(frame, text="Mi carrito",   command=ventana_carrito,   width=18)\
        .grid(row=2, column=0, padx=8, pady=6)
    tk.Button(frame, text="Historial",    command=ventana_historial, width=18)\
        .grid(row=2, column=1, padx=8, pady=6)
    
    global lbl_bienvenida_ref, btn_login_ref
    lbl_bienvenida_ref = lbl_bienvenida
    btn_login_ref = btn_login

    root.after(100, ventana_login)
    root.mainloop()

if __name__ == '__main__':
    iniciar_aplicacion_gui()
