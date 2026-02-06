import unittest
import os
import sqlite3
from server import list_tables, describe_table, read_query, init_db, DB_PATH

class TestDataBaseMCP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure clean state
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()

    @classmethod
    def tearDownClass(cls):
        # Cleanup after tests
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

    def test_list_tables(self):
        result = list_tables()
        self.assertIn("users", result)
        self.assertIn("products", result)

    def test_describe_table(self):
        result = describe_table("users")
        self.assertIn("id (INTEGER)", result)
        self.assertIn("name (TEXT)", result)
        self.assertIn("email (TEXT)", result)
        
        result_error = describe_table("non_existent_table")
        self.assertIn("Error: Table 'non_existent_table' does not exist", result_error)

    def test_read_query_select(self):
        result = read_query("SELECT * FROM users LIMIT 1")
        self.assertIn("Alice Smith", result)
        self.assertIn("alice@example.com", result)

    def test_read_query_forbidden(self):
        forbidden_queries = [
            "INSERT INTO users (name, email) VALUES ('Bad', 'bad@example.com')",
            "DELETE FROM users",
            "DROP TABLE users",
            "UPDATE users SET name='Hacked'"
        ]
        for query in forbidden_queries:
            result = read_query(query)
            self.assertTrue(result.startswith("Error") or "forbidden" in result, f"Failed to block: {query}")

    def test_read_query_not_select(self):
        result = read_query("PRAGMA table_info(users)")
        self.assertIn("Error: Only SELECT queries are allowed", result)

if __name__ == '__main__':
    unittest.main()
