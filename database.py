import sqlite3

conn = sqlite3.connect('users.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')
conn.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin')")
conn.execute("INSERT INTO users (username, password) VALUES ('alice', 'alice123')")
conn.commit()
conn.close()