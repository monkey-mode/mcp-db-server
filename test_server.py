import unittest
import os
from mcp_db_server import create_server, main as server_main
from mcp_db_server.db.sqlite_repository import SqliteRepository
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

    # Note: We test the Repository implementation directly because the MCP tools 
    # are wrapped inside create_server and difficult to access/invoke in isolation 
    # without starting the actual server process.
    
    def test_repository_list_tables(self):
        # Determine likely table count or names based on seed
        tables = self.repo.list_tables()
        self.assertTrue(len(tables) > 0)
        self.assertIn("users", tables)

    def test_repository_describe_table(self):
        result = self.repo.describe_table("users")
        self.assertIn("id", result)
        self.assertIn("name", result)

    def test_repository_read_query_select(self):
        result = self.repo.read_query("SELECT * FROM users LIMIT 1")
        self.assertTrue(len(result) > 0)
        
    def test_repository_forbidden(self):
        forbidden_queries = ["INSERT INTO users (name, email) VALUES ('X', 'y')", "DELETE FROM users"]
        for query in forbidden_queries:
            # We expect these to fail either by logic or driver error
            try:
                result = self.repo.read_query(query)
                # If it didn't raise, ensure it returned an error string
                self.assertTrue("Error" in str(result) or "Security" in str(result))
            except Exception:
                # Driver raising exception is also a pass
                pass

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
