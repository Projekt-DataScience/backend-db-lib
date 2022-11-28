import unittest
from app.models import base
from app.manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):

    def test_database_manager(self):
        DatabaseManager(base, "postgresql://backendgang:backendgang@127.0.0.1:8000/backend")

if __name__ == '__main__':
    unittest.main()