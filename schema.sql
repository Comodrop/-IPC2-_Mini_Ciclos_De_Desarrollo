CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('pendiente','completada')) DEFAULT 'pendiente',
  created_at TEXT,
  updated_at TEXT
);
