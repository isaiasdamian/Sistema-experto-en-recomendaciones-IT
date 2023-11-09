#Autor: Isaias Damian Martinez Rivera
import mysql.connector
import tkinter as tk
from tkinter import messagebox, ttk
from joblib import load
import re
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from joblib import dump, load


df = pd.read_excel('candidatos.xlsx', engine='openpyxl')
X = df[['sskills', 'hskills', 'ingles', 'estudios', 'experiencia']]
y = df['contratado']
X = pd.get_dummies(X, columns=['ingles', 'estudios'])

# Separación de datos en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Entrenamiento del modelo
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluación del modelo
y_pred = clf.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred)}")


# Función para predecir nuevos aplicantes
def predecir_nuevo_aplicante(sskills, hskills, ingles, estudios, experiencia):
    new_data = pd.DataFrame({
        'sskills': [sskills],
        'hskills': [hskills],
        'ingles': [ingles],
        'estudios': [estudios],
        'experiencia': [experiencia]
    })
    new_data = pd.get_dummies(new_data, columns=['ingles', 'estudios']).reindex(columns = X_train.columns, fill_value=0)
    prediction = clf.predict(new_data)
    return 1 if prediction[0] == 1 else 0


rol_actual = None
email_actual = None
nuevo_usuario = None
nueva_password = None
nuevo_rol = None
nuevo_email = None
nombre_usuario = None
apellido_paterno = None
apellido_materno = None
telefono = None
direccion = None
email = None
modo_formulario = "nuevo"
user_logged_in_id = None
id_usuario_combobox = None
vista_general_combobox = None

entry_nombre = None
entry_apellido_paterno = None
entry_apellido_materno = None
entry_telefono = None
entry_direccion = None
entry_ss = None
entry_hs = None
nivel_ingles = None
nivel_estudios = None
entry_yexperience = None


def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="taller_mecanico"
    )



def verificar_usuario(username, password):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, rol, email FROM users WHERE username = %s AND password = %s", (username, password))
    result = cursor.fetchone()
    if result:
        return result[0], result[1], result[2]
    return None, None, None



def login():
    global user_logged_in_id, rol_actual, nuevo_usuario, nueva_password, email_actual
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showerror("Error", "Por favor llena todos los campos.")
        return

    user_id, rol, email = verificar_usuario(username, password)

    if user_id is None or rol is None:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
        return

    user_logged_in_id = user_id 
    rol_actual = rol
    email_actual = email 
    nuevo_usuario = username

    for tab in [tab_usuarios]:
        for widget in tab.winfo_children():
            widget.destroy()

    # Acceso total para "Reclutadores"
    if rol_actual in ["aplicante"]:
        notebook.add(tab_usuarios, text="Usuarios")
    elif rol_actual == "reclutador":
        notebook.add(tab_usuarios_registrados, text="Busqueda de Usuarios")
        notebook.add(tab_vista_general, text="Aplicantes postulados")

    messagebox.showinfo("Bienvenido", f"Bienvenido {username} con rol {rol} e ID = {user_logged_in_id}.")

    usuarios_tab_layout()
    usuarios_registrados_tab_layout()
    vista_general_tab_layout()
    entry_username.delete(0, tk.END)
    entry_password.delete(0, tk.END)

    if nuevo_usuario and nueva_password:
        nuevo_usuario.delete(0, tk.END)
        nueva_password.delete(0, tk.END)
        nuevo_rol.set("")
        nuevo_email.set("")


def logout():
    global user_logged_in_id, rol_actual, nombre_usuario, apellido_paterno, apellido_materno, telefono, direccion, email
    if rol_actual is None:
        messagebox.showwarning("Advertencia", "Ningún usuario ha iniciado sesión.")
        return

    tabs_to_forget = [tab_usuarios, tab_usuarios_registrados, tab_vista_general]
    
    for tab in tabs_to_forget:
        try:
            notebook.index(tab)  
            notebook.forget(tab) 
        except tk.TclError:  
            pass  

    entry_username.delete(0, tk.END)
    entry_password.delete(0, tk.END)
    
    if nombre_usuario:
        nombre_usuario.delete(0, tk.END)
    if apellido_paterno:
        apellido_paterno.delete(0, tk.END)
    if apellido_materno:
        apellido_materno.delete(0, tk.END)
    if telefono:
        telefono.delete(0, tk.END)
    if direccion:
        direccion.delete(0, tk.END)

    rol_actual = None
    user_logged_in_id = None



######################################################-------FUNCIONES BOTONES USUARIOS-----------########################################################################

def buscar_aplicante():
    global search_entry, entry_id, entry_nombre, entry_apellido_paterno, entry_apellido_materno, entry_telefono, entry_direccion, entry_ss, entry_hs, nivel_ingles, nivel_estudios, entry_yexperience
    conn = conectar_db()
    cursor = conn.cursor()
    aplicante_id = search_entry.get() 

    if not aplicante_id:
        messagebox.showerror("Error", "Por favor, introduzca un ID de aplicante para buscar.")
        return

    query = """
    SELECT nombre, apellido_paterno, apellido_materno, telefono, direccion, soft_skills, hard_skills, ingles, estudios, years 
    FROM aplicantes WHERE aplicante_id = %s
    """

    cursor.execute(query, (aplicante_id,))
    result = cursor.fetchone()

    if not result:
        messagebox.showerror("Error", "No se encontró un aplicante con el ID proporcionado.")
        return

    entry_id.delete(0, tk.END)
    entry_id.insert(0, aplicante_id)

    entry_nombre.delete(0, tk.END)
    entry_nombre.insert(0, result[0])
    
    entry_apellido_paterno.delete(0, tk.END)
    entry_apellido_paterno.insert(0, result[1])

    entry_apellido_materno.delete(0, tk.END)
    entry_apellido_materno.insert(0, result[2])

    entry_telefono.delete(0, tk.END)
    entry_telefono.insert(0, result[3])

    entry_direccion.delete(0, tk.END)
    entry_direccion.insert(0, result[4])

    entry_ss.delete(0, tk.END)
    entry_ss.insert(0, result[5])

    entry_hs.delete(0, tk.END)
    entry_hs.insert(0, result[6])

    nivel_ingles.set(result[7])
    nivel_estudios.set(result[8])

    entry_yexperience.delete(0, tk.END)
    entry_yexperience.insert(0, result[9])

    cursor.close()
    conn.close()



def cancelar():
    global modo_formulario  
    
    modo_formulario = "none"  

    entries = [widget for widget in tab_usuarios.winfo_children() if isinstance(widget, tk.Entry)]
    for entry in entries:
        entry.delete(0, tk.END)
        entry['state'] = 'disabled'

    id_buscar_entry = next(widget for widget in tab_usuarios.winfo_children() if isinstance(widget, tk.Entry) and widget.grid_info()['row'] == 0)
    id_buscar_entry['state'] = 'normal'

    for widget in tab_usuarios.winfo_children():
        if isinstance(widget, tk.Button):
            if widget['text'] in ["Guardar", "Cancelar"]:
                widget['state'] = 'normal'
            else:
                widget['state'] = 'disabled'


def cancelar_registro(ventana):
    ventana.destroy()

def signup():
    ventana_registro = tk.Toplevel()
    ventana_registro.title("Registro de nuevo usuario")
    ventana_registro.geometry('370x150')
    screen_width = ventana_registro.winfo_screenwidth()
    screen_height = ventana_registro.winfo_screenheight()

    x = (screen_width / 2) - (370 / 2)  
    y = (screen_height / 2) - (150 / 2)

    ventana_registro.geometry("+%d+%d" % (x, y))

    tk.Label(ventana_registro, text="Nombre de usuario").grid(row=0, column=0)
    entry_username = tk.Entry(ventana_registro, width=40)  
    entry_username.grid(row=0, column=1)

    tk.Label(ventana_registro, text="Contraseña").grid(row=1, column=0)
    entry_password = tk.Entry(ventana_registro, show="*", width=40)  
    entry_password.grid(row=1, column=1)

    tk.Label(ventana_registro, text="Correo electrónico").grid(row=2, column=0)
    entry_email = tk.Entry(ventana_registro, width=40)  
    entry_email.grid(row=2, column=1)

    btn_registrar = tk.Button(ventana_registro, text="Registrar", command=lambda: salvar_usuario(entry_username.get(), entry_password.get(), entry_email.get(), ventana_registro))    
    btn_registrar.grid(row=3, column=0)

    btn_cancelar = tk.Button(ventana_registro, text="Cancelar", command=lambda: cancelar_registro(ventana_registro))
    btn_cancelar.grid(row=3, column=1)


def username_existe(username):
    conn = conectar_db()
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return True if result else False


def salvar_usuario(username, password, email, ventana_registro):
    conn = conectar_db()
    cursor = conn.cursor()

    if username_existe(username):
        messagebox.showerror("Error", "Ya existe un usuario con ese nombre de usuario. Por favor, elige otro.")
        return

    query = "INSERT INTO users (username, password, email, rol) VALUES (%s, %s, %s, 'aplicante')"

    try:
        cursor.execute(query, (username, password, email))
        conn.commit()
        messagebox.showinfo("Información", "Usuario guardado exitosamente.")
        ventana_registro.destroy()
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al guardar el usuario: {e}")

    cursor.close()
    conn.close()



def salvar_aplicante(entry_nombre, entry_apellido_paterno, entry_apellido_materno, entry_telefono, entry_direccion, entry_ss, entry_hs, nivel_ingles, nivel_estudios, entry_yexperience):
    global user_logged_in_id, email_actual, nuevo_usuario, rol_actual
    conn = conectar_db()
    cursor = conn.cursor()

    nombre = entry_nombre.get()
    apellido_paterno = entry_apellido_paterno.get()
    apellido_materno = entry_apellido_materno.get()
    telefono = entry_telefono.get()
    direccion = entry_direccion.get()
    soft_skills = entry_ss.get()
    hard_skills = entry_hs.get()
    ingles = nivel_ingles.get()
    estudios = nivel_estudios.get()
    years = entry_yexperience.get()
    
    username = nuevo_usuario 
    email = email_actual
    user_id = user_logged_in_id
    rol = rol_actual

    recomendado = predecir_nuevo_aplicante(soft_skills, hard_skills, ingles, estudios, years)

    if not user_id:
        messagebox.showerror("Error", "No se pudo encontrar el usuario asociado con el nombre de usuario proporcionado.")
        return

    query = """
    INSERT INTO aplicantes 
    (nombre, apellido_paterno, apellido_materno, telefono, direccion, soft_skills, hard_skills, ingles, estudios, years, user_id, username, email, recomendado) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (nombre, apellido_paterno, apellido_materno, telefono, direccion, soft_skills, hard_skills, ingles, estudios, years, user_id, username, email, recomendado))
        conn.commit()
        messagebox.showinfo("Información", "Gracias por su interes en la vacante, " + ("Paola Valdivia se comunicará con usted a la brevedad" if recomendado == 1 else "nosotros nos comunicaremos con usted"))
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al guardar el aplicante: {e}")

    cursor.close()
    conn.close()

def vista_general_tab_layout():
    global vista_general_combobox
    tk.Label(tab_vista_general, text="Seleccione una opción:").grid(row=0, column=0, pady=10, padx=10, sticky="e")

    opciones = ["Mejores postulantes", "Todos"]
    vista_general_combobox = ttk.Combobox(tab_vista_general, values=opciones)
    vista_general_combobox.grid(row=0, column=1, pady=10, padx=10, sticky="we")

    tk.Button(tab_vista_general, text="Mostrar", command=mostrar_datos).grid(row=1, column=0, pady=10, padx=10)

def mostrar_datos():
    opcion_seleccionada = vista_general_combobox.get()
    
    for widget in tab_vista_general.winfo_children():
        if isinstance(widget, ttk.Treeview):  
            widget.destroy()

    if not opcion_seleccionada: 
        messagebox.showwarning("Advertencia", "Por favor, seleccione una opción.")
        return

    columnas = ["aplicante_id", "nombre", "apellido_paterno", "apellido_materno", "telefono", 
                "username", "direccion", "email", "soft_skills", "hard_skills", "ingles", "estudios", "years"]

    tree = ttk.Treeview(tab_vista_general, columns=columnas, show="headings")
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=65)
    tree.grid(row=2, column=0, columnspan=2, pady=10, padx=10)

    if opcion_seleccionada == "Postulantes recomendados":
        datos = obtener_datos_mejores()
    elif opcion_seleccionada == "Todos los postulantes":
        datos = obtener_datos_todos()
    else:
        messagebox.showwarning("Advertencia", "La opción seleccionada no es válida.")
        return

    for fila in datos:
        tree.insert("", "end", values=fila)

    vista_general_tab_layout()


def obtener_datos_todos():
    conn = conectar_db()
    cursor = conn.cursor()
    query = f"""
    SELECT aplicante_id, nombre, apellido_paterno, apellido_materno, telefono, 
           username, direccion, email, soft_skills, hard_skills, ingles, estudios, years
    FROM aplicantes
    """
    cursor.execute(query)
    datos = cursor.fetchall()
    cursor.close()
    conn.close()
    return datos


def obtener_datos_mejores():
    conn = conectar_db()
    cursor = conn.cursor()
    query = f"""
    SELECT aplicante_id, nombre, apellido_paterno, apellido_materno, telefono, 
           username, direccion, email, soft_skills, hard_skills, ingles, estudios, years
    FROM aplicantes WHERE recomendado = '1'
    """
    cursor.execute(query)
    datos = cursor.fetchall()
    cursor.close()
    conn.close()
    return datos

######################################################-------PESTAÑAS PRINCIPALES-----------########################################################################

def vista_general_tab_layout():
    global vista_general_combobox
    tk.Label(tab_vista_general, text="Seleccione una opción:").grid(row=0, column=0, pady=10, padx=10, sticky="e")

    opciones = ["Postulantes recomendados", "Todos los postulantes"]
    vista_general_combobox = ttk.Combobox(tab_vista_general, values=opciones)
    vista_general_combobox.grid(row=0, column=1, pady=10, padx=10, sticky="we")

    tk.Button(tab_vista_general, text="Mostrar", command=mostrar_datos).grid(row=1, column=0, pady=10, padx=10)


def usuarios_tab_layout():

    row = 1
    tk.Label(tab_usuarios, text="Nombres:").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    entry_nombre = tk.Entry(tab_usuarios)
    entry_nombre.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 1
    tk.Label(tab_usuarios, text="Apellido Paterno").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    entry_apellido_paterno = tk.Entry(tab_usuarios)
    entry_apellido_paterno.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 1
    tk.Label(tab_usuarios, text="Apellido Materno").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    entry_apellido_materno = tk.Entry(tab_usuarios)
    entry_apellido_materno.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 1
    tk.Label(tab_usuarios, text="Telefono").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    entry_telefono = tk.Entry(tab_usuarios)
    entry_telefono.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 1
    tk.Label(tab_usuarios, text="Dirección").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    entry_direccion = tk.Entry(tab_usuarios)
    entry_direccion.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 1
    tk.Label(tab_usuarios, text="% Soft Skills:").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    entry_ss = tk.Entry(tab_usuarios)
    entry_ss.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 1
    tk.Label(tab_usuarios, text="% Hard Skills:").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    entry_hs = tk.Entry(tab_usuarios)
    entry_hs.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 1
    tk.Label(tab_usuarios, text="Nivel de ingles:").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    nivel_ingles = ttk.Combobox(tab_usuarios, values=["A1", "A2", "B1", "B2", "C1", "C2"])
    nivel_ingles.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 1
    tk.Label(tab_usuarios, text="Nivel de estudios:").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    nivel_estudios = ttk.Combobox(tab_usuarios, values=["Preparatoria", "Licenciatura", "Maestría", "Doctorado"])
    nivel_estudios.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 1
    tk.Label(tab_usuarios, text="Años de experiencia:").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    entry_yexperience = tk.Entry(tab_usuarios)
    entry_yexperience.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 2  
    btn_guardar = tk.Button(tab_usuarios, text="Guardar", command=lambda: salvar_aplicante(entry_nombre, entry_apellido_paterno, entry_apellido_materno, entry_telefono, entry_direccion, entry_ss, entry_hs, nivel_ingles, nivel_estudios, entry_yexperience),
                        width=15, height=2)
    btn_guardar.grid(row=row, column=1, padx=10, pady=10, sticky="w")  

    #btn_cancelar = tk.Button(tab_usuarios, text="Cancelar", command=cancelar, width=15, height=2)
    #btn_cancelar.grid(row=row, column=1, padx=10, pady=10, sticky="w")  

    tab_usuarios.grid_columnconfigure(1, weight=3)
    tab_usuarios.grid_columnconfigure(3, weight=1)
    tab_usuarios.grid_columnconfigure(0, weight=1)

    for widget in tab_usuarios.winfo_children():
        widget.grid(padx=5, pady=5)

def usuarios_registrados_tab_layout():
    global search_entry, entry_id, entry_nombre, entry_apellido_paterno, entry_apellido_materno, entry_telefono, entry_direccion, entry_ss, entry_hs, nivel_ingles, nivel_estudios, entry_yexperience

    tk.Label(tab_usuarios_registrados, text="Ingrese ID a Buscar").grid(row=0, column=0, pady=10, padx=10, sticky="e")
    search_entry = tk.Entry(tab_usuarios_registrados)
    search_entry.grid(row=0, column=1, pady=10, padx=10, columnspan=2, sticky="we")
    tk.Button(tab_usuarios_registrados, text="Buscar", command=buscar_aplicante).grid(row=0, column=3, pady=10, padx=10)

    row = 1

    tk.Label(tab_usuarios_registrados, text="ID").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    entry_id = tk.Entry(tab_usuarios_registrados)
    entry_id.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 1
    tk.Label(tab_usuarios_registrados, text="Nombres:").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    entry_nombre = tk.Entry(tab_usuarios_registrados)
    entry_nombre.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 1
    tk.Label(tab_usuarios_registrados, text="Apellido Paterno").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    entry_apellido_paterno = tk.Entry(tab_usuarios_registrados)
    entry_apellido_paterno.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 1
    tk.Label(tab_usuarios_registrados, text="Apellido Materno").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    entry_apellido_materno = tk.Entry(tab_usuarios_registrados)
    entry_apellido_materno.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 1
    tk.Label(tab_usuarios_registrados, text="Telefono").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    entry_telefono = tk.Entry(tab_usuarios_registrados)
    entry_telefono.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 1
    tk.Label(tab_usuarios_registrados, text="Dirección").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    entry_direccion = tk.Entry(tab_usuarios_registrados)
    entry_direccion.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 1
    tk.Label(tab_usuarios_registrados, text="% Soft Skills:").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    entry_ss = tk.Entry(tab_usuarios_registrados)
    entry_ss.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 1
    tk.Label(tab_usuarios_registrados, text="% Hard Skills:").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    entry_hs = tk.Entry(tab_usuarios_registrados)
    entry_hs.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 1
    tk.Label(tab_usuarios_registrados, text="Nivel de ingles:").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    nivel_ingles = ttk.Combobox(tab_usuarios_registrados, values=["A1", "A2", "B1", "B2", "C1", "C2"])
    nivel_ingles.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 1
    tk.Label(tab_usuarios_registrados, text="Nivel de estudios:").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    nivel_estudios = ttk.Combobox(tab_usuarios_registrados, values=["Preparatoria", "Licenciatura", "Maestría", "Doctorado"])
    nivel_estudios.grid(row=row, column=1, pady=5, padx=5, sticky="we")

    row += 1
    tk.Label(tab_usuarios_registrados, text="Años de experiencia:").grid(row=row, column=0, pady=5, padx=5, sticky="e")
    entry_yexperience = tk.Entry(tab_usuarios_registrados)
    entry_yexperience.grid(row=row, column=1, pady=5, padx=5, sticky="we")


    tab_usuarios_registrados.grid_columnconfigure(1, weight=3)
    tab_usuarios_registrados.grid_columnconfigure(3, weight=1)
    tab_usuarios_registrados.grid_columnconfigure(0, weight=1)

    for widget in tab_usuarios_registrados.winfo_children():
        widget.grid(padx=5, pady=5)

######################################################-------VENTANA PRINCIPAL -----------########################################################################

window = tk.Tk()
window.title("Sistema Experto en recomendaciones IT")
window.geometry('1365x735')

notebook = ttk.Notebook(window)
notebook.pack(fill='both', expand=True)

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

x = (screen_width / 2) - (1365 / 2)
y = (screen_height / 2) - (735 / 2)

window.geometry("+%d+%d" % (x, y))

window.resizable(False, False)
tab_login = ttk.Frame(notebook)
notebook.add(tab_login, text="Login")

tk.Label(tab_login, text="Nombre de usuario").pack()
entry_username = tk.Entry(tab_login)
entry_username.pack()

tk.Label(tab_login, text="Contraseña").pack()
entry_password = tk.Entry(tab_login, show="*")
entry_password.pack()

tk.Button(tab_login, text="Iniciar sesión", command=login).pack()
tk.Button(tab_login, text="Cerrar Sesión", command=logout).pack()
tk.Button(tab_login, text="Registrar Usuario", command= signup).pack()


tab_usuarios = ttk.Frame(notebook)
tab_usuarios_registrados = ttk.Frame(notebook)
tab_vista_general = ttk.Frame(notebook)


window.mainloop()
