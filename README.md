# MCP Database Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server implementation in Python that provides **strictly read-only** access to databases. It allows Large Language Models (LLMs) to inspect schemas and query data safely without risking data modification.

## Features

- **🛡️ Strict Read-Only**: Enforced at the driver level (e.g., SQLite `?mode=ro`). Write operations (INSERT, UPDATE, DELETE) are blocked by the database engine itself.
- **🏗️ Repository Pattern**: Abstracted database access allows for easy extension to other backends (PostgreSQL, MySQL) via Dependency Injection.
- **⚡ FastMCP**: Built efficiently using the official MCP Python SDK.
- **🔧 Easy Configuration**: Managed via environment variables and Makefiles.

## Project Structure

- `server.py`: Main entry point for the MCP server.
- `db/`: Contains the Repository interface and implementations.
- `seed.py`: Utility script to populate the database (since the server itself is read-only).
- `Makefile`: Automation for common tasks.

## Quick Start

### Prerequisites
- Python 3.10+
- `make` (optional, but recommended)

### 1. Setup
Use the Makefile to create a virtual environment, install dependencies, and seed a test database:

```bash
make setup
```

*This runs `pip install -r requirements.txt` and `python seed.py`.*

### 2. Configuration
The project uses `python-dotenv`. Copy the example config and adjust as needed:

```bash
cp .env.example .env
```

**Key Variables:**
- `DB_ENGINE`: `sqlite` (Default)
- `DB_ADDRESS`: Path to db file (for SQLite) or Host URL.
- `DB_USER` / `DB_PASSWORD`: (For future Postgres support).

### 3. Run the Server
Start the MCP server:

```bash
make run
```
*(Or directly via `venv/bin/python server.py`)*

## Usage with LLMs

Once running, the server exposes the following tools to connected MCP clients:

1.  **`list_tables()`**
    - Returns a list of all tables in the database.
2.  **`describe_table(table_name: str)`**
    - Returns the schema (columns, types, primary keys) for the specified table.
3.  **`read_query(query: str)`**
    - Executes a SQL `SELECT` query.
    - **Note**: Queries attempting to modify data will raise a `Security Error` or `OperationalError`.

## Development

### Running Tests
Execute the unit test suite:

```bash
make test
```

### Extending
To add support for a new database (e.g., Postgres):
1.  Create `db/postgres_repository.py` implementation of `DatabaseRepository`.
2.  Update `server.py` to instantiate it when `DB_ENGINE=postgres`.
