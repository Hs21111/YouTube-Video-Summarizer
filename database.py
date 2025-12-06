import sqlite3
import datetime

DB_NAME = "chat_history.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Table for storing video metadata
    c.execute('''CREATE TABLE IF NOT EXISTS videos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  youtube_id TEXT UNIQUE,
                  title TEXT,
                  transcript TEXT,
                  created_at TIMESTAMP)''')
    
    # Table for storing chat messages
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  video_id INTEGER,
                  role TEXT,
                  content TEXT,
                  timestamp TIMESTAMP,
                  FOREIGN KEY(video_id) REFERENCES videos(id))''')
    conn.commit()
    conn.close()

def save_video(youtube_id, title, transcript):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO videos (youtube_id, title, transcript, created_at) VALUES (?, ?, ?, ?)",
                  (youtube_id, title, transcript, datetime.datetime.now()))
        conn.commit()
        video_id = c.lastrowid
    except sqlite3.IntegrityError:
        # If already exists, return the existing ID
        c.execute("SELECT id FROM videos WHERE youtube_id = ?", (youtube_id,))
        video_id = c.fetchone()[0]
    finally:
        conn.close()
    return video_id

def get_video(youtube_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, title, transcript FROM videos WHERE youtube_id = ?", (youtube_id,))
    result = c.fetchone()
    conn.close()
    return result

def get_video_by_id(pk):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, youtube_id, title, transcript FROM videos WHERE id = ?", (pk,))
    result = c.fetchone()
    conn.close()
    return result

def get_all_videos():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, youtube_id, title FROM videos ORDER BY created_at DESC")
    results = c.fetchall()
    conn.close()
    return results

def add_message(video_id, role, content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO messages (video_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
              (video_id, role, content, datetime.datetime.now()))
    conn.commit()
    conn.close()

def get_chat_history(video_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE video_id = ? ORDER BY timestamp ASC", (video_id,))
    results = c.fetchall()
    conn.close()
    return results
