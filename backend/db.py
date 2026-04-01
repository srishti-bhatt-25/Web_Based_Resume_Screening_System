import sqlite3

def get_db():
    return sqlite3.connect("database.db")

def init_db():
    conn = get_db()
    c = conn.cursor()

    # USERS TABLE
    c.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )''')

    # 🔥 ADD LINKEDIN COLUMN IF NOT EXISTS
    try:
        c.execute("ALTER TABLE users ADD COLUMN linkedin TEXT")
    except:
        pass

    # JOBS TABLE
    c.execute('''CREATE TABLE IF NOT EXISTS jobs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        dsl TEXT
    )''')

    # APPLICATIONS TABLE
    c.execute('''CREATE TABLE IF NOT EXISTS applications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        job_id INTEGER,
        status TEXT
    )''')

    conn.commit()
    conn.close()