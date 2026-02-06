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
    from dotenv import load_dotenv
    load_dotenv()

    # Read config
    db_engine = os.getenv("DB_ENGINE", "sqlite")
    # For SQLite, address is the file path
    db_address = os.getenv("DB_ADDRESS", "test.db")
    
    # Credentials (unused for SQLite but ready for Postgres)
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_schema = os.getenv("DB_SCHEMA")

    try:
        repo = None
        if db_engine.lower() == "sqlite":
            repo = SqliteRepository(db_address)
        # elif db_engine.lower() == "postgres":
        #     repo = PostgresRepository(db_address, db_user, db_password, db_schema)
        else:
            raise ValueError(f"Unsupported DB_ENGINE: {db_engine}")

        mcp = create_server(repo)
        mcp.run()
    except Exception as e:
        print(f"Error starting server: {e}")
