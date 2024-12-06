from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from datetime import datetime
from typing import List

app = FastAPI()

# SQLite Database Initialization
def initialize_database():
    db = sqlite3.connect("memotime.db")
    cursor = db.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tbl_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tbl_timers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT NOT NULL,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        duration INTEGER
    )
    """)

    db.commit()
    cursor.close()
    db.close()

# Initialize the database when the app starts
initialize_database()

# Database Connection
def get_db_connection():
    return sqlite3.connect("memotime.db")

# Models for Pydantic
class Note(BaseModel):
    title: str
    content: str

class Timer(BaseModel):
    task_name: str
    start_time: datetime
    end_time: datetime

# Notes Management

@app.post("/notes/")
def create_note(note: Note):
    db = get_db_connection()
    cursor = db.cursor()
    query = "INSERT INTO tbl_notes (title, content, created_at, updated_at) VALUES (?, ?, datetime('now'), datetime('now'))"
    cursor.execute(query, (note.title, note.content))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Note created successfully"}

@app.get("/notes/")
def get_all_notes():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tbl_notes")
    notes = [dict(id=row[0], title=row[1], content=row[2], created_at=row[3], updated_at=row[4]) for row in cursor.fetchall()]
    cursor.close()
    db.close()
    return notes

@app.get("/notes/{note_id}")
def get_note_by_id(note_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tbl_notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()
    cursor.close()
    db.close()
    if row:
        return dict(id=row[0], title=row[1], content=row[2], created_at=row[3], updated_at=row[4])
    raise HTTPException(status_code=404, detail="Note not found")

@app.put("/notes/{note_id}")
def update_note(note_id: int, note: Note):
    db = get_db_connection()
    cursor = db.cursor()
    query = "UPDATE tbl_notes SET title = ?, content = ?, updated_at = datetime('now') WHERE id = ?"
    cursor.execute(query, (note.title, note.content, note_id))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Note updated successfully"}

@app.delete("/notes/{note_id}")
def delete_note_by_id(note_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM tbl_notes WHERE id = ?", (note_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Note deleted successfully"}

@app.get("/notes/search/")
def search_notes_by_title(title: str):
    db = get_db_connection()
    cursor = db.cursor()
    query = "SELECT * FROM tbl_notes WHERE title LIKE ?"
    cursor.execute(query, ('%' + title + '%',))
    notes = [dict(id=row[0], title=row[1], content=row[2], created_at=row[3], updated_at=row[4]) for row in cursor.fetchall()]
    cursor.close()
    db.close()
    return notes

@app.get("/notes/count/")
def get_note_count():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM tbl_notes")
    count = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return {"total_notes": count}

@app.get("/notes/recent/")
def get_recently_updated_notes():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tbl_notes ORDER BY updated_at DESC LIMIT 5")
    notes = [dict(id=row[0], title=row[1], content=row[2], created_at=row[3], updated_at=row[4]) for row in cursor.fetchall()]
    cursor.close()
    db.close()
    return notes

@app.delete("/notes/bulk-delete/")
def bulk_delete_notes(ids: List[int]):
    db = get_db_connection()
    cursor = db.cursor()
    format_strings = ','.join(['?'] * len(ids))
    cursor.execute(f"DELETE FROM tbl_notes WHERE id IN ({format_strings})", tuple(ids))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Notes deleted successfully"}

# Timer Management

@app.post("/timers/")
def create_timer(timer: Timer):
    db = get_db_connection()
    cursor = db.cursor()
    duration = int((timer.end_time - timer.start_time).total_seconds())
    query = "INSERT INTO tbl_timers (task_name, start_time, end_time, duration) VALUES (?, ?, ?, ?)"
    cursor.execute(query, (timer.task_name, timer.start_time, timer.end_time, duration))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Timer created successfully"}

@app.get("/timers/")
def get_all_timers():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tbl_timers")
    timers = [dict(id=row[0], task_name=row[1], start_time=row[2], end_time=row[3], duration=row[4]) for row in cursor.fetchall()]
    cursor.close()
    db.close()
    return timers

@app.get("/timers/{timer_id}")
def get_timer_by_id(timer_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tbl_timers WHERE id = ?", (timer_id,))
    row = cursor.fetchone()
    cursor.close()
    db.close()
    if row:
        return dict(id=row[0], task_name=row[1], start_time=row[2], end_time=row[3], duration=row[4])
    raise HTTPException(status_code=404, detail="Timer not found")

@app.put("/timers/{timer_id}")
def update_timer(timer_id: int, timer: Timer):
    db = get_db_connection()
    cursor = db.cursor()
    duration = int((timer.end_time - timer.start_time).total_seconds())
    query = "UPDATE tbl_timers SET task_name = ?, start_time = ?, end_time = ?, duration = ? WHERE id = ?"
    cursor.execute(query, (timer.task_name, timer.start_time, timer.end_time, duration, timer_id))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Timer updated successfully"}

@app.delete("/timers/{timer_id}")
def delete_timer_by_id(timer_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM tbl_timers WHERE id = ?", (timer_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Timer deleted successfully"}

@app.get("/timers/active/")
def get_active_timers():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tbl_timers WHERE end_time IS NULL")
    timers = [dict(id=row[0], task_name=row[1], start_time=row[2], end_time=row[3], duration=row[4]) for row in cursor.fetchall()]
    cursor.close()
    db.close()
    return timers

# Timer Management

@app.post("/timers/")
def create_timer(timer: Timer):
    db = get_db_connection()
    cursor = db.cursor()
    duration = int((timer.end_time - timer.start_time).total_seconds())
    query = """
        INSERT INTO tbl_timers (task_name, start_time, end_time, duration)
        VALUES (?, ?, ?, ?)
    """
    cursor.execute(query, (timer.task_name, timer.start_time, timer.end_time, duration))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Timer created successfully"}

@app.get("/timers/")
def get_all_timers():
    db = get_db_connection()
    cursor = db.cursor()
    query = "SELECT * FROM tbl_timers"
    cursor.execute(query)
    timers = cursor.fetchall()
    cursor.close()
    db.close()
    # Convert results to a list of dictionaries
    keys = ["id", "task_name", "start_time", "end_time", "duration"]
    return [dict(zip(keys, timer)) for timer in timers]

@app.get("/timers/{timer_id}")
def get_timer_by_id(timer_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    query = "SELECT * FROM tbl_timers WHERE id = ?"
    cursor.execute(query, (timer_id,))
    timer = cursor.fetchone()
    cursor.close()
    db.close()
    if timer:
        keys = ["id", "task_name", "start_time", "end_time", "duration"]
        return dict(zip(keys, timer))
    raise HTTPException(status_code=404, detail="Timer not found")

@app.put("/timers/{timer_id}")
def update_timer(timer_id: int, timer: Timer):
    db = get_db_connection()
    cursor = db.cursor()
    duration = int((timer.end_time - timer.start_time).total_seconds())
    query = """
        UPDATE tbl_timers
        SET task_name = ?, start_time = ?, end_time = ?, duration = ?
        WHERE id = ?
    """
    cursor.execute(query, (timer.task_name, timer.start_time, timer.end_time, duration, timer_id))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Timer updated successfully"}

@app.delete("/timers/{timer_id}")
def delete_timer_by_id(timer_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    query = "DELETE FROM tbl_timers WHERE id = ?"
    cursor.execute(query, (timer_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Timer deleted successfully"}

@app.get("/timers/active/")
def get_active_timers():
    db = get_db_connection()
    cursor = db.cursor()
    query = "SELECT * FROM tbl_timers WHERE end_time IS NULL"
    cursor.execute(query)
    timers = cursor.fetchall()
    cursor.close()
    db.close()
    keys = ["id", "task_name", "start_time", "end_time", "duration"]
    return [dict(zip(keys, timer)) for timer in timers]

@app.get("/timers/duration/")
def calculate_total_time(task_name: str):
    db = get_db_connection()
    cursor = db.cursor()
    query = "SELECT SUM(duration) FROM tbl_timers WHERE task_name = ?"
    cursor.execute(query, (task_name,))
    total_duration = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return {"total_duration_seconds": total_duration}

@app.get("/timers/average-duration/")
def get_average_duration():
    db = get_db_connection()
    cursor = db.cursor()
    query = "SELECT AVG(duration) FROM tbl_timers"
    cursor.execute(query)
    avg_duration = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return {"average_duration_seconds": avg_duration}

@app.get("/timers/range/")
def get_timers_in_range(start: datetime, end: datetime):
    db = get_db_connection()
    cursor = db.cursor()
    query = """
        SELECT * FROM tbl_timers
        WHERE start_time BETWEEN ? AND ?
    """
    cursor.execute(query, (start, end))
    timers = cursor.fetchall()
    cursor.close()
    db.close()
    keys = ["id", "task_name", "start_time", "end_time", "duration"]
    return [dict(zip(keys, timer)) for timer in timers]
