#intefaz base de datos
import tkinter as tk
import psycopg

def ventana_buscar():
    vent_buscar = tk.Tk()
    vent_buscar.title("busqueda")
    vent_buscar.geometry("400x400")
    
    #elementos ventana_buscar
    etiqueta_titulo = tk.Label(vent_buscar, text="¿Qué tipo de busqueda desea realizar?")
    etiqueta_titulo.place(x=90,y=30)

    boton_por_juego = tk.Button(vent_buscar, text="Por juego")
    boton_por_juego.place(x=100, y=100)
    
    boton_por_usuario = tk.Button(vent_buscar, text="Por usuario")
    boton_por_usuario.place(x=220, y=100)
    
    entrada_busqueda= tk.Entry(vent_buscar)
    entrada_busqueda.place(x=100, y=200)

    boton_confirmar = tk.Button(vent_buscar, text="buscar")
    boton_confirmar.place(x=220, y=200)

def ventana_agregar():
    def agr_juego():
        vent_agr_juego = tk.Toplevel()
        vent_agr_juego.title("Añadir juego")
        vent_agr_juego.geometry("400x400")

        #elementos ventana agregar juegos
        instruccion_juego = tk.Label(vent_agr_juego, text="Información de ingreso para el juego")
        instruccion_juego.place(x=90, y=30)

        text_nombre = tk.Label(vent_agr_juego, text="Titulo del juego: ")
        text_nombre.place(x=10,y=80)
        
        entry_titulo = tk.Entry(vent_agr_juego)
        entry_titulo.place(x=105,y=80)
        
        text_descripcion_juego = tk.Label(vent_agr_juego, text="Descripción del juego: ")
        text_descripcion_juego.place(x=10,y=130)

        entry_descripcion_juego = tk.Entry(vent_agr_juego)
        entry_descripcion_juego.place(x=135,y=130)

        text_desarrollador = tk.Label(vent_agr_juego, text="Desarrollador: ")
        text_desarrollador.place(x=10,y=180)

        entry_desarrollador = tk.Entry(vent_agr_juego)
        entry_desarrollador.place(x=92,y=180)

        text_precio = tk.Label(vent_agr_juego, text="Precio: ")
        text_precio.place(x=10,y=230)

        entry_precio = tk.Entry(vent_agr_juego)
        entry_precio.place(x=55,y=230)

        text_fe_lanzamiento = tk.Label(vent_agr_juego, text="Fecha de lanzamiento: ")
        text_fe_lanzamiento.place(x=10,y=280)

        entry_fe_lanzamiento = tk.Entry(vent_agr_juego)
        entry_fe_lanzamiento.place(x=137,y=280)
    
    def agr_usuario():
        vent_agr_usuario = tk.Toplevel()
        vent_agr_usuario.title("Añadir Usuario")
        vent_agr_usuario.geometry("400x400")
        
        instruccion_usuario = tk.Label(vent_agr_usuario, text="Información para el ingreso del usuario")
        instruccion_usuario.place(x=90, y=30)

        #elementos ventana agregar usuario

        text_nombre = tk.Label(vent_agr_usuario, text="Nombre usuario: ")
        text_nombre.place(x=10,y=80)
        
        entry_nombre = tk.Entry(vent_agr_usuario)
        entry_nombre.place(x=108,y=80)
        
        text_correo = tk.Label(vent_agr_usuario, text="Correo usuario: ")
        text_correo.place(x=10,y=130)

        entry_correo = tk.Entry(vent_agr_usuario)
        entry_correo.place(x=100,y=130)

        text_contrasena = tk.Label(vent_agr_usuario, text="contraseña: ")
        text_contrasena.place(x=10,y=180)

        entry_contrasena = tk.Entry(vent_agr_usuario)
        entry_contrasena.place(x=80,y=180)

        text_saldo = tk.Label(vent_agr_usuario, text="Saldo disponible: ")
        text_saldo.place(x=10,y=230)

        entry_saldo = tk.Entry(vent_agr_usuario)
        entry_saldo.place(x=110,y=230)

        text_fe_registro = tk.Label(vent_agr_usuario, text="Fecha de registro: ")
        text_fe_registro.place(x=10,y=280)

        entry_fe_registro = tk.Entry(vent_agr_usuario)
        entry_fe_registro.place(x=112,y=280)

    def agr_logro():

        #def test():
        #    print(marcado.get())
        
        vent_agr_logro = tk.Toplevel()
        vent_agr_logro.title("Añadir logro")
        vent_agr_logro.geometry("400x400")

        instruccion_logro = tk.Label(vent_agr_logro, text="Información para el ingreso de logro")
        instruccion_logro.place(x=90,y=30)

        #elementos de ventana agregar logro

        text_nombre_logro = tk.Label(vent_agr_logro, text="Nombre del logro: ")
        text_nombre_logro.place(x=10,y=80)
        
        entry_nombre_logro = tk.Entry(vent_agr_logro)
        entry_nombre_logro.place(x=116,y=80)
        
        text_descripcion_logro = tk.Label(vent_agr_logro, text="Descripción del logro: ")
        text_descripcion_logro.place(x=10,y=130)

        entry_descripcion_logro = tk.Entry(vent_agr_logro)
        entry_descripcion_logro.place(x=134,y=130)
        
        text_url_icono = tk.Label(vent_agr_logro, text="Url logro: ")
        text_url_icono.place(x=10,y=180)

        entry_url_icono = tk.Entry(vent_agr_logro)
        entry_url_icono.place(x=68,y=180)

        text_es_oculto = tk.Label(vent_agr_logro, text="¿Es oculto? ")
        text_es_oculto.place(x=10,y=230)
        
        marcado=tk.BooleanVar()
        checkbox = tk.Checkbutton(vent_agr_logro, variable=marcado)
        checkbox.place(x=77,y=230)
        
        #ejemplo = tk.Button(vent_agr_logro, command=test)
        #ejemplo.place(x=90, y=230)

    vent_agregar= tk.Toplevel()
    vent_agregar.title("Agregar")
    vent_agregar.geometry("400x400")

    instruccion_agregar = tk.Label(vent_agregar, text="¿Qué información desea agregar?")
    instruccion_agregar.place(x=90, y=30)
    
    boton_in_juego = tk.Button(vent_agregar, text="Juego", command=agr_juego)
    boton_in_juego.place(x=90,y=80)

    boton_in_juego = tk.Button(vent_agregar, text="Usuario", command=agr_usuario)
    boton_in_juego.place(x=160,y=80)

    boton_in_juego = tk.Button(vent_agregar, text="Logro", command=agr_logro)
    boton_in_juego.place(x=230,y=80)

#ventana principal
root = tk.Tk()
root.title("Base de datos")
root.geometry("500x400")

#elementos ventana principal
boton_agregar = tk.Button(root, text="agregar", command=ventana_agregar)
boton_agregar.place(x=200, y=200)

boton_buscar = tk.Button(root, text="buscar", command=ventana_buscar)
boton_buscar.place(x=280, y=200)

boton_eliminar = tk.Button(root, text="eliminar")
boton_eliminar.place(x=200, y=240 )

root.mainloop()