from abc import ABC, abstractmethod
from typing import List, Union

class DatabaseRepository(ABC):
    @abstractmethod
    def list_tables(self) -> List[str]:
        """List all tables in the database."""
        pass

    @abstractmethod
    def describe_table(self, table_name: str) -> str:
        """Get schema information for a specific table."""
        pass

    @abstractmethod
    def read_query(self, query: str) -> str:
        """
        Execute a read-only query.
        Returns a formatted string (table) or an error string.
        """
        pass
