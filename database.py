import sqlite3
import pickle
import datetime

def get_connection():
    return sqlite3.connect('hostel_db.sqlite', check_same_thread=False)

def init_db():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        roll TEXT,
        room TEXT,
        encoding BLOB,
        image BLOB
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        name TEXT,
        action TEXT,
        timestamp TEXT
    )
    """)
    con.commit()
    con.close()

def add_student(name, roll, room, encoding, image_bytes):
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO students (name, roll, room, encoding, image) VALUES (?, ?, ?, ?, ?)",
                (name, roll, room, pickle.dumps(encoding), image_bytes))
    con.commit()
    con.close()

def get_all_students():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT id, name, roll, room, encoding, image FROM students")
    rows = cur.fetchall()
    students = []
    for r in rows:
        students.append({
            'id': r[0], 'name': r[1], 'roll': r[2], 'room': r[3], 'encoding': pickle.loads(r[4]), 'image': r[5]
        })
    con.close()
    return students

def add_log(student_id, name, action):
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO logs (student_id, name, action, timestamp) VALUES (?, ?, ?, ?)",
                (student_id, name, action, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    con.commit()
    con.close()

def get_logs():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM logs ORDER BY timestamp DESC")
    rows = cur.fetchall()
    con.close()
    return rows

def get_last_action(student_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT action FROM logs WHERE student_id=? ORDER BY timestamp DESC LIMIT 1", (student_id,))
    r = cur.fetchone()
    con.close()
    if r:
        return r[0]
    return None

def update_student(student_id, name, roll, room, image_bytes=None):
    con = get_connection()
    cur = con.cursor()
    if image_bytes is not None:
        cur.execute("UPDATE students SET name=?, roll=?, room=?, image=? WHERE id=?",
                    (name, roll, room, image_bytes, student_id))
    else:
        cur.execute("UPDATE students SET name=?, roll=?, room=? WHERE id=?",
                    (name, roll, room, student_id))
    con.commit()
    con.close()
