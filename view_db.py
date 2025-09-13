import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect("tasks.db")
cursor = conn.cursor()

# Consultar todas las tareas
cursor.execute("SELECT * FROM tasks")
rows = cursor.fetchall()

print("📋 Tareas en la base de datos:")
for row in rows:
    print(row)

conn.close()
