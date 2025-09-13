import sqlite3
# Importa el módulo sqlite3 para trabajar con bases de datos SQLite

# Conexión a la base (crea tasks.db si no existe)
conn = sqlite3.connect("tasks.db")
cur = conn.cursor()
# Se conecta (o crea) la base de datos 'tasks.db' y obtiene un cursor para ejecutar SQL

# Leer el script desde schema.sql
with open("schema.sql", "r") as f:
    sql_script = f.read()
# Abre el archivo schema.sql en modo lectura y guarda todo su contenido en sql_script

cur.executescript(sql_script)  # Ejecuta todo el contenido del archivo SQL
conn.commit()                  # Guarda los cambios en la base de datos
conn.close()                   # Cierra la conexión con la base de datos

print("Base de datos inicializada con schema.sql")
# Mensaje indicando que la base de datos fue creada o inicializada

#!/usr/bin/env python3
"""
todo_app.py
To-Do List simple con SQLite y GUI en tkinter/ttk.
Crea tasks.db en el mismo directorio si no existe.
"""
# Encabezado y docstring explicando el propósito del script

import sqlite3
import datetime
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
# Importa librerías: sqlite3 para DB, datetime para timestamps,
# os para operaciones del sistema de archivos,
# tkinter y ttk para la interfaz gráfica,
# messagebox y simpledialog para mostrar diálogos emergentes

DB_FILE = "tasks.db"
# Define la variable global con el nombre de la base de datos

# ---------------------------
# Funciones de ayuda para la base de datos
# ---------------------------
def get_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn
# Devuelve una conexión a la base de datos tasks.db

def init_db():
    conn = get_connection()         # Obtiene la conexión
    cur = conn.cursor()             # Crea un cursor para ejecutar SQL
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('pendiente','completada')) DEFAULT 'pendiente',
        created_at TEXT,
        updated_at TEXT
    )
    """)
    conn.commit()   # Guarda cambios
    conn.close()    # Cierra la conexión
# Crea la tabla 'tasks' si no existe con campos: id, title, status, created_at, updated_at

def add_task(title):
    if not title or title.strip() == "":
        raise ValueError("El título no puede estar vacío.")
    # Verifica que el título no esté vacío
    now = datetime.datetime.utcnow().isoformat()  # Fecha y hora actual en formato ISO
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (title, status, created_at, updated_at) VALUES (?,?,?,?)",
                (title.strip(), "pendiente", now, now))
    conn.commit()                  # Guarda los cambios
    task_id = cur.lastrowid         # Obtiene el ID asignado automáticamente
    conn.close()
    return task_id                  # Devuelve el ID de la tarea agregada

def list_tasks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, status, created_at, updated_at FROM tasks ORDER BY id")
    rows = cur.fetchall()           # Devuelve todas las filas como lista de tuplas
    conn.close()
    return rows

def mark_completed(task_id):
    now = datetime.datetime.utcnow().isoformat()  # Fecha y hora actual
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET status = 'completada', updated_at = ? WHERE id = ?", (now, task_id))
    conn.commit()
    conn.close()
# Marca una tarea como completada y actualiza la fecha de modificación

def edit_task(task_id, new_id, new_title, new_status, new_created, new_updated):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE tasks
        SET id = ?, title = ?, status = ?, created_at = ?, updated_at = ?
        WHERE id = ?
    """, (new_id, new_title.strip(), new_status, new_created, new_updated, task_id))
    conn.commit()
    conn.close()
# Permite editar todos los campos de una tarea, incluyendo ID y fechas

def delete_task(task_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
# Elimina una tarea según su ID

# ---------------------------
# Interfaz gráfica (GUI)
# ---------------------------
class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mini To-Do (IA + SQLite + GitHub)")
        self.geometry("700x420")       # Tamaño de la ventana
        self.configure(padx=10, pady=10)  # Padding interno
        self.create_widgets()          # Crear todos los widgets
        self.refresh_tasks()           # Cargar tareas en el Treeview

    def create_widgets(self):
        frm_top = ttk.Frame(self)      # Frame superior para Entry y botones
        frm_top.pack(fill="x", pady=(0,8))

        ttk.Label(frm_top, text="Título tarea:").pack(side="left", padx=(0,6))
        self.entry_title = ttk.Entry(frm_top)       # Entry para escribir título
        self.entry_title.pack(side="left", fill="x", expand=True)

        btn_add = ttk.Button(frm_top, text="Agregar", command=self.on_add)
        btn_add.pack(side="left", padx=6)
        # Botón para agregar tarea

        btn_mark = ttk.Button(frm_top, text="Marcar completada", command=self.on_mark_completed)
        btn_mark.pack(side="left", padx=6)
        # Botón para marcar tarea como completada

        btn_edit = ttk.Button(frm_top, text="Editar", command=self.on_edit)
        btn_edit.pack(side="left", padx=6)
        # Botón para editar tarea

        btn_delete = ttk.Button(frm_top, text="Eliminar", command=self.on_delete)
        btn_delete.pack(side="left", padx=6)
        # Botón para eliminar tarea

        # Treeview para mostrar la lista de tareas
        cols = ("id", "title", "status", "created_at", "updated_at")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", selectmode="browse")
        # Definir encabezados y tamaño de columnas
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=40, anchor="center")
        self.tree.heading("title", text="Título")
        self.tree.column("title", width=300, anchor="w")
        self.tree.heading("status", text="Estado")
        self.tree.column("status", width=100, anchor="center")
        self.tree.heading("created_at", text="Creado")
        self.tree.column("created_at", width=130, anchor="center")
        self.tree.heading("updated_at", text="Actualizado")
        self.tree.column("updated_at", width=130, anchor="center")
        self.tree.pack(fill="both", expand=True)

        # Frame inferior (footer) para botones y contador
        frm_footer = ttk.Frame(self)
        frm_footer.pack(fill="x", pady=(8,0))
        self.lbl_count = ttk.Label(frm_footer, text="Tareas: 0")
        self.lbl_count.pack(side="left")  # Contador de tareas

        btn_refresh = ttk.Button(frm_footer, text="Refrescar", command=self.refresh_tasks)
        btn_refresh.pack(side="right")  # Botón para refrescar Treeview
        
        btn_listar_popup = ttk.Button(frm_footer, text="Listar tareas (popup)", command=self.on_list_tasks)
        btn_listar_popup.pack(side="right", padx=6)
        # Botón para listar tareas en un mensaje emergente
        
        


    # ---------------------------
    # Event handlers
    # ---------------------------
    def on_add(self):
        title = self.entry_title.get()
        try:
            tid = add_task(title)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self.entry_title.delete(0, tk.END)  # Limpia el Entry
        self.refresh_tasks()                # Refresca Treeview
        messagebox.showinfo("Agregado", f"Tarea agregada con id {tid}")

    def get_selected_task_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        item = self.tree.item(sel[0])
        return item["values"][0]
    # Devuelve el ID de la tarea seleccionada

    def on_mark_completed(self):
        tid = self.get_selected_task_id()
        if not tid:
            messagebox.showwarning("Atención", "Selecciona una tarea.")
            return
        mark_completed(tid)
        self.refresh_tasks()
    # Marca la tarea seleccionada como completada

    def on_edit(self):
        tid = self.get_selected_task_id()
        if not tid:
            messagebox.showwarning("Atención", "Selecciona una tarea.")
            return

        item = self.tree.item(self.tree.selection()[0])
        current_id = item["values"][0]
        current_title = item["values"][1]
        current_status = item["values"][2]
        current_created = item["values"][3]
        current_updated = item["values"][4]

        # Pedir nuevos valores mediante diálogos
        new_id = simpledialog.askinteger("Editar tarea", "Nuevo ID:", initialvalue=current_id, parent=self)
        new_title = simpledialog.askstring("Editar tarea", "Nuevo título:", initialvalue=current_title, parent=self)
        new_status = simpledialog.askstring("Editar tarea", "Nuevo estado (pendiente/completada):",
                                            initialvalue=current_status, parent=self)
        new_created = simpledialog.askstring("Editar tarea", "Fecha creado (ISO):", initialvalue=current_created, parent=self)
        new_updated = simpledialog.askstring("Editar tarea", "Fecha actualizado (ISO):", initialvalue=current_updated, parent=self)

        if not new_title or new_title.strip() == "":
            messagebox.showerror("Error", "El título no puede estar vacío.")
            return
        if new_status not in ("pendiente", "completada"):
            messagebox.showerror("Error", "Estado inválido. Usa 'pendiente' o 'completada'.")
            return

        edit_task(tid, new_id, new_title, new_status, new_created, new_updated)
        self.refresh_tasks()
    # Permite editar todos los campos de la tarea seleccionada

    def on_delete(self):
        tid = self.get_selected_task_id()
        if not tid:
            messagebox.showwarning("Atención", "Selecciona una tarea.")
            return
        if messagebox.askyesno("Eliminar", "¿Eliminar tarea seleccionada?"):
            delete_task(tid)
            self.refresh_tasks()
    # Elimina la tarea seleccionada con confirmación

    def refresh_tasks(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = list_tasks()
        for row in rows:
            self.tree.insert("", "end", values=row)
        self.lbl_count.config(text=f"Tareas: {len(rows)}")
    # Refresca la vista del Treeview y actualiza el contador

    def on_list_tasks(self):
        rows = list_tasks()
        if not rows:
            messagebox.showinfo("Lista de Tareas", "No hay tareas registradas.")
            return

        msg = ""
        for row in rows:
            msg += f"ID: {row[0]}\nTítulo: {row[1]}\nEstado: {row[2]}\nCreado: {row[3]}\nActualizado: {row[4]}\n\n"

        messagebox.showinfo("Lista de Tareas", msg)
    # Muestra todas las tareas en un mensaje emergente
    
    def on_list_tasks(self):
        rows = list_tasks()  # Llama a la función que ya tienes
        if not rows:
            messagebox.showinfo("Lista de Tareas", "No hay tareas registradas.")
            return

        # Crear ventana emergente propia
        popup = tk.Toplevel(self)
        popup.title("Lista de Tareas")
        popup.geometry("500x400")  # Tamaño de la ventana
        popup.transient(self)      # Modal relativo a la ventana principal
        popup.grab_set()           # Bloquea interacción con ventana principal

        # Frame para text + scrollbar
        frame = ttk.Frame(popup)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Widget Text para mostrar las tareas
        text = tk.Text(frame, wrap="none")  # wrap="none" para no cortar líneas
        text.pack(side="left", fill="both", expand=True)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        scrollbar.pack(side="right", fill="y")
        text.configure(yscrollcommand=scrollbar.set)

        # Llenar el Text con todas las tareas
        for row in rows:
            text.insert("end", f"ID: {row[0]}\nTítulo: {row[1]}\nEstado: {row[2]}\nCreado: {row[3]}\nActualizado: {row[4]}\n\n")

        text.config(state="disabled")  # Evita que el usuario edite el contenido


# ---------------------------
# Main
# ---------------------------
def main():
    init_db()          # Inicializa la base de datos
    app = TodoApp()    # Crea la ventana principal
    app.mainloop()     # Ejecuta el bucle principal de tkinter

if __name__ == "__main__":
    main()
# Si el script se ejecuta directamente, llama a main()
