# MCP Database Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server implementation in Python that provides **strictly read-only** access to databases. It allows Large Language Models (LLMs) to inspect schemas and query data safely without risking data modification.

## Features

- **🛡️ Strict Read-Only**: Enforced at the driver level (e.g., SQLite `?mode=ro`) or session level (MySQL `SET SESSION TRANSACTION READ ONLY`).
- **🏗️ Repository Pattern**: Abstracted database access allows for easy extension to other backends (PostgreSQL, MySQL) via Dependency Injection.
- **⚡ FastMCP**: Built efficiently using the official MCP Python SDK.
- **🔌 Connection Pooling**: Automatic connection pooling for MySQL using `DBUtils` to ensure performance and reliability.
- **🔧 Easy Configuration**: Managed via environment variables and Makefiles.

## Project Structure

- `mcp_db/`: Main Python package for the MCP server.
  - `__init__.py`: Entry point and server initialization.
  - `db/`: Repository implementations (`sqlite_repository.py`, `mysql_repository.py`).
- `seed.py`: Utility script to populate the database (write access).
- `Makefile`: Automation for common tasks.
- `pyproject.toml`: Package configuration and dependencies.

## Quick Start

### Prerequisites
- Python 3.12+ (managed via `venv`)
- `make` (optional, but recommended)
- MySQL Server (optional, if using MySQL backend)

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
- `DB_ENGINE`: `sqlite` (Default) or `mysql`
- `DB_ADDRESS`: Path to db file (SQLite) or Host URL (MySQL).
- `DB_PORT`: Database port (Default: 3306 for MySQL).
- `DB_USER` / `DB_PASSWORD`: Database credentials (required for MySQL).
- `DB_SCHEMA`: Database name (required for MySQL).

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
