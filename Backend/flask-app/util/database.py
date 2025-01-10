import sqlite3
import traceback

class SQLiteContextManager:
    """
    A context manager for managing SQLite database connections.
    """
    def __init__(self, db_path):
        self.db_path = db_path

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_path)
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            print(f"Database Exception: {exc_type}, {exc_value}")
            traceback.print_tb(traceback)
        self.connection.commit()
        self.connection.close()


class AppDatabaseContextManager(SQLiteContextManager):
    """
    Context manager for the application's main database.
    """
    def __init__(self, db_path='data/app_database.db'):
        super().__init__(db_path)


class SafetyMapDatabaseContextManager(SQLiteContextManager):
    """
    Context manager for the safety map database.
    """
    def __init__(self):
        super().__init__('data/safety_map.db')
