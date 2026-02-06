from mcp.server.fastmcp import FastMCP
import sqlite3
import os

# Initialize FastMCP server
mcp = FastMCP("db-server")

DB_PATH = "test.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with some sample data if it doesn't exist."""
    if not os.path.exists(DB_PATH):
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

@mcp.tool()
def list_tables() -> str:
    """List all tables in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row['name'] for row in cursor.fetchall()]
    conn.close()
    return "Tables: " + ", ".join(tables)

@mcp.tool()
def describe_table(table_name: str) -> str:
    """Get the schema information for a specific table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if table exists to prevent injection via table name in other queries if we were doing dynamic SQL construction carelessly,
    # distinct from parameter binding. For execution of PRAGMA, parameter binding might not work as expected in all drivers, 
    # but here we use f-string with simple validation check first is safer.
    # Actually sqlite3 library doesn't support placeholders for table names.
    # So we validate against list_tables first.
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row['name'] for row in cursor.fetchall()]
    
    if table_name not in tables:
        conn.close()
        return f"Error: Table '{table_name}' does not exist."
        
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    conn.close()
    
    schema = []
    for col in columns:
        # cid, name, type, notnull, dflt_value, pk
        col_str = f"- {col['name']} ({col['type']})"
        if col['pk']:
            col_str += " [PK]"
        schema.append(col_str)
        
    return f"Schema for {table_name}:\n" + "\n".join(schema)

@mcp.tool()
def read_query(query: str) -> str:
    """
    Execute a read-only SQL query (SELECT). 
    Strictly forbids INSERT, UPDATE, DELETE, DROP, ALTER, etc.
    """
    normalized_query = query.strip().upper()
    if not normalized_query.startswith("SELECT"):
        return "Error: Only SELECT queries are allowed."
    
    forbidden_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "REPLACE"]
    for word in forbidden_keywords:
        if word in normalized_query:
             # This is a naive check. A robust system would parse the SQL AST.
             # but for this demo, this simple check prevents obvious misuse.
            return f"Error: Query contains forbidden keyword '{word}'."

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return "No results found."
            
        # Format results
        output = []
        # Get column names
        # cursor.description is (name, type_code, display_size, internal_size, precision, scale, null_ok)
        if cursor.description:
            col_names = [desc[0] for desc in cursor.description]
            output.append(" | ".join(col_names))
            output.append("-" * len(" | ".join(col_names)))
            
        for row in results:
            row_str = " | ".join(str(item) for item in row)
            output.append(row_str)
            
        return "\n".join(output)
        
    except sqlite3.Error as e:
        return f"Database Error: {e}"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    init_db()
    # mcp.run() is generally used for stdio transport
    mcp.run()
