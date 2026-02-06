import sqlite3
import os
from typing import List
from .repository import DatabaseRepository

class SqliteRepository(DatabaseRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

    def _get_connection(self):
        # Enforce read-only mode at driver level
        return sqlite3.connect(f"file:{os.path.abspath(self.db_path)}?mode=ro", uri=True)

    def list_tables(self) -> List[str]:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tables
        except Exception as e:
            return [f"Error listing tables: {e}"]

    def describe_table(self, table_name: str) -> str:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Validate table existence first
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            if table_name not in tables:
                conn.close()
                return f"Error: Table '{table_name}' does not exist."
                
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            conn.close()
            
            schema = []
            for col in columns:
                # PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
                col_name = col[1]
                col_type = col[2]
                pk = col[5]
                
                col_str = f"- {col_name} ({col_type})"
                if pk:
                    col_str += " [PK]"
                schema.append(col_str)
                
            return f"Schema for {table_name}:\n" + "\n".join(schema)
            
        except Exception as e:
            return f"Error describing table: {e}"

    def read_query(self, query: str) -> str:
        normalized_query = query.strip().upper()
        if not normalized_query.startswith("SELECT"):
            return "Error: Only SELECT queries are allowed."
        
        # Double check forbidden keywords (defense in depth)
        forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "REPLACE"]
        for word in forbidden:
            if word in normalized_query:
                return f"Error: Query contains forbidden keyword '{word}'."

        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            
            output = []
            if cursor.description:
                col_names = [desc[0] for desc in cursor.description]
                output.append(" | ".join(col_names))
                output.append("-" * len(" | ".join(col_names)))
                
            conn.close()
            
            if not results:
                return "No results found."

            for row in results:
                row_str = " | ".join(str(item) for item in row)
                output.append(row_str)
                
            return "\n".join(output)
            
        except sqlite3.OperationalError as e:
            if "readonly" in str(e):
                return f"Security Error: Attempted write operation on read-only database."
            return f"Database Error: {e}"
        except Exception as e:
            return f"Error: {e}"
