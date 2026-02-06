import sqlite3
import os

DB_PATH = "test.db"

def init_db():
    """Initialize the database with some sample data if it doesn't exist."""
    print(f"Initializing {DB_PATH}...")
    if os.path.exists(DB_PATH):
        print(f"{DB_PATH} already exists.")
        # Optional: remove it to force fresh start
        # os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Create Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    
    # Insert sample data
    cursor.executemany('INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)', [
        ('Alice Smith', 'alice@example.com'),
        ('Bob Jones', 'bob@example.com'),
        ('Charlie Brown', 'charlie@example.com')
    ])
    
    cursor.executemany('INSERT OR IGNORE INTO products (name, price, stock) VALUES (?, ?, ?)', [
        ('Laptop', 999.99, 10),
        ('Mouse', 25.50, 50),
        ('Monitor', 199.99, 20)
    ])
    
    conn.commit()
    conn.close()
    print(f"Initialized {DB_PATH} with sample data.")

if __name__ == "__main__":
    init_db()
