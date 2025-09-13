import sqlite3

def init_db():
    # Conexión: crea el archivo tasks.db si no existe
    conn = sqlite3.connect("tasks.db")
    cur = conn.cursor()

    # Leer y ejecutar el script schema.sql
    with open("schema.sql", "r", encoding="utf-8") as f:
        sql_script = f.read()

    cur.executescript(sql_script)
    conn.commit()
    conn.close()
    print("✅ Base de datos creada/validada con éxito (tasks.db).")

if __name__ == "__main__":
    init_db()
