from mcp.server.fastmcp import FastMCP
from db.repository import DatabaseRepository
from db.sqlite_repository import SqliteRepository

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
    # Default to SQLite for standalone run
    # In a real app, you might parse args or env vars to choose repository
    db_path = "test.db"
    try:
        repo = SqliteRepository(db_path)
        mcp = create_server(repo)
        mcp.run()
    except FileNotFoundError:
        print(f"Error: Database file '{db_path}' not found. Please run 'seed.py' first.")
    except Exception as e:
        print(f"Error starting server: {e}")
