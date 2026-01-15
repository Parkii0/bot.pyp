import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'bot_data.db')

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Channels/Groups table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            chat_id INTEGER,
            title TEXT,
            chat_type TEXT,
            auto_accept INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            UNIQUE(user_id, chat_id)
        )
    ''')
    
    # Pending join requests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pending_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            user_id INTEGER,
            first_name TEXT,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(chat_id, user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name):
    """Add or update a user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
    ''', (user_id, username, first_name))
    conn.commit()
    conn.close()

def add_channel(user_id, chat_id, title, chat_type):
    """Add a channel/group for a user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO channels (user_id, chat_id, title, chat_type)
            VALUES (?, ?, ?, ?)
        ''', (user_id, chat_id, title, chat_type))
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    conn.close()
    return result

def get_user_channels(user_id):
    """Get all channels/groups for a user"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM channels WHERE user_id = ?
    ''', (user_id,))
    channels = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return channels

def get_channel(user_id, chat_id):
    """Get a specific channel"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM channels WHERE user_id = ? AND chat_id = ?
    ''', (user_id, chat_id))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_channel(user_id, chat_id):
    """Delete a channel/group"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM channels WHERE user_id = ? AND chat_id = ?
    ''', (user_id, chat_id))
    conn.commit()
    conn.close()

def toggle_auto_accept(user_id, chat_id):
    """Toggle auto accept for a channel"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE channels SET auto_accept = CASE WHEN auto_accept = 0 THEN 1 ELSE 0 END
        WHERE user_id = ? AND chat_id = ?
    ''', (user_id, chat_id))
    conn.commit()
    
    cursor.execute('''
        SELECT auto_accept FROM channels WHERE user_id = ? AND chat_id = ?
    ''', (user_id, chat_id))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def get_auto_accept_channels():
    """Get all channels with auto accept enabled"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM channels WHERE auto_accept = 1
    ''')
    channels = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return channels

def add_pending_request(chat_id, user_id, first_name, username):
    """Add a pending join request"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO pending_requests (chat_id, user_id, first_name, username)
            VALUES (?, ?, ?, ?)
        ''', (chat_id, user_id, first_name, username))
        conn.commit()
        result = True
    except:
        result = False
    conn.close()
    return result

def get_pending_requests(chat_id, limit=None):
    """Get pending requests for a chat"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if limit:
        cursor.execute('''
            SELECT * FROM pending_requests WHERE chat_id = ? ORDER BY created_at ASC LIMIT ?
        ''', (chat_id, limit))
    else:
        cursor.execute('''
            SELECT * FROM pending_requests WHERE chat_id = ? ORDER BY created_at ASC
        ''', (chat_id,))
    requests = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return requests

def delete_pending_request(chat_id, user_id):
    """Delete a pending request after accepting"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM pending_requests WHERE chat_id = ? AND user_id = ?
    ''', (chat_id, user_id))
    conn.commit()
    conn.close()

def get_pending_count(chat_id):
    """Get count of pending requests for a chat"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM pending_requests WHERE chat_id = ?
    ''', (chat_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

# Initialize database on import
init_db()
