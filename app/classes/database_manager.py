from flask_bcrypt import Bcrypt
import sqlite3


class DatabaseManager:
    def __init__(self, db_path="Roomies.db"):
        self.db_path = db_path
        self.bcrypt = Bcrypt()
        self.tables = ["Roommates", "RoommateGroups", "Pairing", "Task", "Event"]

    def connect_db(self):
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            return None

    # manually dropping tables (in case, we modify tables)
    def drop_db(self):
        try:
            with self.connect_db() as conn:
                for table in self.tables:
                    conn.execute(f"DROP TABLE IF EXISTS {table};")
        except sqlite3.Error as e:
            print(f"Error dropping database tables: {e}")
            return False
        return True

    # wipe data in tables (manual for now, automate later)
    def clear_db(self):
        try:
            with self.connect_db() as conn:
                for table in self.tables:
                    conn.execute(f"DELETE FROM {table};")
        except sqlite3.Error as e:
            print(f"Error clearing database tables: {e}")
            return False
        return True

    def create_db(self):
        try:
            with self.connect_db() as conn:
                # users table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS Roommates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        code TEXT
                    );
                    """
                )
                # groups table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS RoommateGroups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        group_name TEXT NOT NULL, 
                        code TEXT NOT NULL UNIQUE
                    );
                    """
                )
                # users-group association
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS Pairing (
                        user_id INTEGER NOT NULL,
                        group_id INTEGER NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES Roommates(id),
                        FOREIGN KEY (group_id) REFERENCES RoommateGroups(id),
                        UNIQUE(user_id, group_id)
                    );
                    """
                )

                # tasks table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS Task(
                        taskId INTEGER PRIMARY KEY AUTOINCREMENT,
                        assignedTo INTEGER NOT NULL,
                        dueDate TEXT NOT NULL,
                        dateCreated TEXT NOT NULL,
                        priority INTEGER,
                        createdBy INTEGER NOT NULL,
                        completed INTEGER NOT NULL,
                        accepted INTEGER NOT NULL,
                        description TEXT NOT NULL,
                        groupId INTEGER NOT NULL,
                        FOREIGN KEY(assignedTo) REFERENCES Roommates(id),
                        FOREIGN KEY(createdBy) REFERENCES Roommates(id),
                        FOREIGN KEY(groupId) REFERENCES RoommateGroups(id)
                    );
                    """
                )

                # Events table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS Event(
                        eventId INTEGER PRIMARY KEY AUTOINCREMENT,
                        dueDate TEXT NOT NULL,
                        dateCreated TEXT NOT NULL,
                        createdBy INTEGER NOT NULL,
                        description TEXT NOT NULL,
                        groupId INTEGER NOT NULL,
                        FOREIGN KEY(createdBy) REFERENCES Roommates(id),
                        FOREIGN KEY(groupId) REFERENCES RoommateGroups(id)
                    );
                    """
                )

        except sqlite3.Error as e:
            print(f"Error creating database tables: {e}")
            return False
        return True

    def initialize_db(self, drop=False, clear=False):
        # drops tables before creating if needed
        if drop:
            if not self.drop_db():
                print(f"Failed to drop tables.")
                return False
        # create tables
        if not self.create_db():
            print(f"Failed to create tables.")
            return False
        # clear tables if needed
        if clear:
            if not self.clear_db():
                print(f"Failed to clear tables.")
                return False
        return True


class DatabaseMixin:
    @classmethod
    def get_by_id(cls, user_id):
        db_manager = DatabaseManager()
        try:
            with db_manager.connect_db() as conn:
                cursor = conn.execute(
                    f"""SELECT * FROM {cls.TABLE_NAME} WHERE id = ?""", (user_id,)
                )
                row = cursor.fetchone()
                cursor.close()
                if row is None:
                    return None
                return cls.from_db_row(row)
        except sqlite3.Error as e:
            print(f"Error obtaining record: {e}")
            return None
