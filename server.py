from mcp.server.fastmcp import FastMCP
from db.repository import DatabaseRepository
import os

def create_server(repository: DatabaseRepository) -> FastMCP:
    mcp = FastMCP("db-server")

    @mcp.tool()
    def list_tables() -> str:
        """List all tables in the database."""
        tables = repository.list_tables()
        if not tables:
            return "No tables found or error occurred."
        return "Tables: " + ", ".join(tables)

    @mcp.tool()
    def describe_table(table_name: str) -> str:
        """Get the schema information for a specific table."""
        return repository.describe_table(table_name)

    @mcp.tool()
    def read_query(query: str) -> str:
        """
        Execute a read-only SQL query (SELECT). 
        Strictly forbids INSERT, UPDATE, DELETE, DROP, ALTER, etc.
        """
        return repository.read_query(query)
        
    return mcp

if __name__ == "__main__":
    from dotenv import load_dotenv
    from db.sqlite_repository import SqliteRepository
    from db.mysql_repository import MysqlRepository

    load_dotenv()

    # Read config
    db_engine = os.getenv("DB_ENGINE", "sqlite")
    db_address = os.getenv("DB_ADDRESS", "test.db")
    db_port = int(os.getenv("DB_PORT", 3306))
    
    # Credentials (unused for SQLite)
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_schema = os.getenv("DB_SCHEMA")

    try:
        repo = None
        if db_engine.lower() == "sqlite":
            repo = SqliteRepository(db_address)
        elif db_engine.lower() == "mysql":
             repo = MysqlRepository(
                 host=db_address,
                 user=db_user,
                 password=db_password,
                 database=db_schema,
                 port=db_port
             )
        else:
            raise ValueError(f"Unsupported DB_ENGINE: {db_engine}")

        mcp = create_server(repo)
        mcp.run()
    except Exception as e:
        print(f"Error starting server: {e}")
