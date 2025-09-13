import sqlite3

# Conexión a la base (crea tasks.db si no existe)
conn = sqlite3.connect("tasks.db")
cur = conn.cursor()

# Leer el script desde schema.sql
with open("schema.sql", "r") as f:
    sql_script = f.read()

cur.executescript(sql_script)  # Ejecuta todo el contenido del archivo
conn.commit()
conn.close()

print("Base de datos inicializada con schema.sql")


#!/usr/bin/env python3
"""
todo_app.py
To-Do List simple con SQLite y GUI en tkinter/ttk.
Crea tasks.db en el mismo directorio si no existe.
"""

import sqlite3
import datetime
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

DB_FILE = "tasks.db"

# ---------------------------
# Database helpers
# ---------------------------
def get_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('pendiente','completada')) DEFAULT 'pendiente',
        created_at TEXT,
        updated_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_task(title):
    if not title or title.strip() == "":
        raise ValueError("El título no puede estar vacío.")
    now = datetime.datetime.utcnow().isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (title, status, created_at, updated_at) VALUES (?,?,?,?)",
                (title.strip(), "pendiente", now, now))
    conn.commit()
    task_id = cur.lastrowid
    conn.close()
    return task_id

def list_tasks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, status, created_at, updated_at FROM tasks ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows

def mark_completed(task_id):
    now = datetime.datetime.utcnow().isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET status = 'completada', updated_at = ? WHERE id = ?", (now, task_id))
    conn.commit()
    conn.close()

def edit_task(task_id, new_title):
    now = datetime.datetime.utcnow().isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET title = ?, updated_at = ? WHERE id = ?", (new_title.strip(), now, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

# ---------------------------
# GUI Application
# ---------------------------
class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mini To-Do (IA + SQLite + GitHub)")
        self.geometry("700x420")
        self.configure(padx=10, pady=10)
        self.create_widgets()
        self.refresh_tasks()

    def create_widgets(self):
        frm_top = ttk.Frame(self)
        frm_top.pack(fill="x", pady=(0,8))

        ttk.Label(frm_top, text="Título tarea:").pack(side="left", padx=(0,6))
        self.entry_title = ttk.Entry(frm_top)
        self.entry_title.pack(side="left", fill="x", expand=True)

        btn_add = ttk.Button(frm_top, text="Agregar", command=self.on_add)
        btn_add.pack(side="left", padx=6)

        btn_mark = ttk.Button(frm_top, text="Marcar completada", command=self.on_mark_completed)
        btn_mark.pack(side="left", padx=6)

        btn_edit = ttk.Button(frm_top, text="Editar", command=self.on_edit)
        btn_edit.pack(side="left", padx=6)

        btn_delete = ttk.Button(frm_top, text="Eliminar", command=self.on_delete)
        btn_delete.pack(side="left", padx=6)

        # Treeview
        cols = ("id", "title", "status", "created_at", "updated_at")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", selectmode="browse")
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

        # Footer
        frm_footer = ttk.Frame(self)
        frm_footer.pack(fill="x", pady=(8,0))
        self.lbl_count = ttk.Label(frm_footer, text="Tareas: 0")
        self.lbl_count.pack(side="left")

        btn_refresh = ttk.Button(frm_footer, text="Refrescar", command=self.refresh_tasks)
        btn_refresh.pack(side="right")

    # Event handlers
    def on_add(self):
        title = self.entry_title.get()
        try:
            tid = add_task(title)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self.entry_title.delete(0, tk.END)
        self.refresh_tasks()
        messagebox.showinfo("Agregado", f"Tarea agregada con id {tid}")

    def get_selected_task_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        item = self.tree.item(sel[0])
        return item["values"][0]

    def on_mark_completed(self):
        tid = self.get_selected_task_id()
        if not tid:
            messagebox.showwarning("Atención", "Selecciona una tarea.")
            return
        mark_completed(tid)
        self.refresh_tasks()

    def on_edit(self):
        tid = self.get_selected_task_id()
        if not tid:
            messagebox.showwarning("Atención", "Selecciona una tarea.")
            return
        item = self.tree.item(self.tree.selection()[0])
        current_title = item["values"][1]
        new_title = simpledialog.askstring("Editar tarea", "Nuevo título:", initialvalue=current_title, parent=self)
        if new_title and new_title.strip() != "":
            edit_task(tid, new_title)
            self.refresh_tasks()

    def on_delete(self):
        tid = self.get_selected_task_id()
        if not tid:
            messagebox.showwarning("Atención", "Selecciona una tarea.")
            return
        if messagebox.askyesno("Eliminar", "¿Eliminar tarea seleccionada?"):
            delete_task(tid)
            self.refresh_tasks()

    def refresh_tasks(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = list_tasks()
        for row in rows:
            self.tree.insert("", "end", values=row)
        self.lbl_count.config(text=f"Tareas: {len(rows)}")

# ---------------------------
# Main
# ---------------------------
def main():
    init_db()
    app = TodoApp()
    app.mainloop()

if __name__ == "__main__":
    main()
