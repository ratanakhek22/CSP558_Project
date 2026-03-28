import sqlite3
 
conn = sqlite3.connect('users.db')
 
conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')
 
# INSERT OR IGNORE prevents duplicate entries on re-runs
conn.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'admin')")
conn.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('alice', 'alice123')")
 
conn.commit()
conn.close()
 
print("Database initialized.")
 