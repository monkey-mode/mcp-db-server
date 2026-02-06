import pymysql
import os
from typing import List, Union
from .repository import DatabaseRepository

from dbutils.pooled_db import PooledDB

class MysqlRepository(DatabaseRepository):
    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        
        # Initialize connection pool
        # mincached=2, maxcached=5 are reasonable defaults
        self.pool = PooledDB(
            creator=pymysql,
            mincached=2,
            maxcached=5,
            blocking=True,  # Wait for connection if pool is empty
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port,
            cursorclass=pymysql.cursors.Cursor
        )

    def _get_connection(self):
        # Get connection from pool
        return self.pool.connection()

    def list_tables(self) -> List[str]:
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                 cursor.execute("SHOW TABLES")
                 # result is tuple of tuples
                 tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tables
        except Exception as e:
            return [f"Error listing tables: {e}"]

    def describe_table(self, table_name: str) -> str:
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                # Validate table exists (prevent injection)
                cursor.execute("SHOW TABLES")
                tables = [row[0] for row in cursor.fetchall()]
                if table_name not in tables:
                    return f"Error: Table '{table_name}' does not exist."

                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
            conn.close()

            schema = []
            # Field, Type, Null, Key, Default, Extra
            for col in columns:
                col_name = col[0]
                col_type = col[1]
                key = col[3]
                
                col_str = f"- {col_name} ({col_type})"
                if key == 'PRI':
                    col_str += " [PK]"
                schema.append(col_str)

            return f"Schema for {table_name}:\n" + "\n".join(schema)
        except Exception as e:
            return f"Error describing table: {e}"

    def read_query(self, query: str) -> str:
        normalized_query = query.strip().upper()
        if not normalized_query.startswith("SELECT"):
            return "Error: Only SELECT queries are allowed."

        try:
            conn = self._get_connection()
            try:
                with conn.cursor() as cursor:
                    # Enforce Read Only mode for this session
                    cursor.execute("SET SESSION TRANSACTION READ ONLY")
                    
                    cursor.execute(query)
                    results = cursor.fetchall()

                    output = []
                    if cursor.description:
                        col_names = [desc[0] for desc in cursor.description]
                        output.append(" | ".join(col_names))
                        output.append("-" * len(" | ".join(col_names)))

                    if not results:
                        return "No results found."

                    for row in results:
                        row_str = " | ".join(str(item) for item in row)
                        output.append(row_str)

                    return "\n".join(output)
            finally:
                conn.close()

        except pymysql.OperationalError as e:
            # Code 1290 is The MySQL server is running with the --read-only option so it cannot execute this statement
            # Or similar for session read only
            if e.args[0] == 1792: # Cannot execute statement in a READ ONLY transaction.
                 return "Security Error: Attempted write operation in read-only mode."
            return f"Database Error: {e}"
        except Exception as e:
            return f"Error: {e}"
