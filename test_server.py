import unittest
import os
from server import create_server
from db.sqlite_repository import SqliteRepository
from seed import init_db, DB_PATH

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

    def setUp(self):
        self.repo = SqliteRepository(DB_PATH)
        # We can't easily invoke mcp tools directly without running the server or accessing the internal registry
        # But FastMCP tools are decorated functions.
        # However, create_server returns the mcp instance.
        # FastMCP instance tool decorators register the function.
        # We need to access the decorated functions.
        # In FastMCP, mcp.tool() returns the original function but registers it side-effectually?
        # Actually FastMCP 0.1.x implementation: @mcp.tool() returns the function wrapper.
        
        # Let's verify by just testing the repository directly for logic, 
        # AND testing the server construction.
        # For unit testing the "server wrapper", we can trust FastMCP works if we pass the right data.
        # So we should focus on testing the Repository implementation and the interaction flow if possible.
        pass

    def test_repository_list_tables(self):
        tables = self.repo.list_tables()
        self.assertIn("users", tables)
        self.assertIn("products", tables)

    def test_repository_describe_table(self):
        result = self.repo.describe_table("users")
        self.assertIn("id (INTEGER)", result)
        self.assertIn("name (TEXT)", result)
        
        result_error = self.repo.describe_table("non_existent_table")
        self.assertIn("Error: Table 'non_existent_table' does not exist", result_error)

    def test_repository_read_query_select(self):
        result = self.repo.read_query("SELECT * FROM users LIMIT 1")
        self.assertIn("Alice Smith", result)
        
    def test_repository_forbidden(self):
        forbidden_queries = ["INSERT INTO users (name, email) VALUES ('X', 'y')", "DELETE FROM users"]
        for query in forbidden_queries:
            result = self.repo.read_query(query)
            # It might be blocked by "Only SELECT..." OR "Security Error" (if it got past check)
            self.assertTrue("Error" in result or "Security Error" in result, f"Failed to block: {result}")

    def test_repository_allowed_forbidden_words(self):
        """Test that we can now use words like INSERT/UPDATE in a valid SELECT."""
        # This would have failed with the old keyword check
        result = self.repo.read_query("SELECT 'INSERT', 'UPDATE'")
        self.assertIn("INSERT", result)
        self.assertIn("UPDATE", result)

    def test_repository_readonly_driver_enforcement(self):
        # Similar to previous test, but utilizing the repository's internal connection logic
        # We need to access the protected _get_connection to test raw execution if read_query blocks it
        # Or we rely on read_query's protection.
        # To strictly test the driver read-only mode, we can try to hack it via _get_connection
        # purely to assert our configuration is correct.
        conn = self.repo._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("CREATE TABLE hack (id int)")
            self.fail("Driver allowed write!")
        except Exception as e:
            self.assertTrue("readonly" in str(e).lower())
        finally:
            conn.close()

if __name__ == '__main__':
    unittest.main()
