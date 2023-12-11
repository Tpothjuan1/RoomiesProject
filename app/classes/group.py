import uuid
import sqlite3
from .database_manager import DatabaseManager, DatabaseMixin


class Group(DatabaseMixin):
    TABLE_NAME = "RoommateGroups"

    def __init__(self, group_name, code=None):
        self.id = None
        self.group_name = group_name
        self.code = None
        self.db_manager = DatabaseManager()

    def save_to_db(self):
        try:
            with self.db_manager.connect_db() as conn:
                if self.id is None:
                    # UUID should be unique, but just to make sure...
                    unique_code = self.code
                    while unique_code is None:
                        temp_code = str(uuid.uuid4())
                        if self.is_code_unique(temp_code):
                            unique_code = temp_code
                        self.code = unique_code
                    cursor = conn.execute(
                        """
                        INSERT INTO RoommateGroups (group_name, code) VALUES (?, ?)
                        """, (self.group_name, self.code)
                    )
                    conn.commit()
                    self.id = cursor.lastrowid
                else:
                    conn.execute(
                        """
                        UPDATE RoommateGroups
                        SET group_name = ?, code = ?
                        WHERE id = ?
                        """,
                        (self.group_name, self.code, self.id)
                    )
                    conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving group: {e}")
            return None

    def add_roommate(self, roommate):
        try:
            with self.db_manager.connect_db() as conn:
                conn.execute(
                    """
                    INSERT INTO Pairing (user_id, group_id)
                    VALUES (?, ?)
                    """,
                    (roommate.id, self.id)
                )
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding roommate to group: {e}")
            return None

    def remove_roommate(self, roommate):
        try:
            with self.db_manager.connect_db() as conn:
                conn.execute(
                    """
                    DELETE FROM Pairing
                    WHERE user_id = ? AND group_id = ?
                    """,
                    (roommate.id, self.id)
                )
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error removing roommate from group: {e}")
            return None

    def get_roommates(self):
        from .roommate import Roommate
        try:
            with self.db_manager.connect_db() as conn:
                cursor = conn.execute(
                    """
                    SELECT r.* FROM Roommates r
                    JOIN Pairing p ON r.id = p.user_id
                    WHERE p.group_id = ?
                    """,
                    (self.id,)
                )
                roommates = [Roommate.from_db_row(row) for row in cursor.fetchall()]
                cursor.close()
            return roommates
        except sqlite3.Error as e:
            print(f"Error fetching roommates for group: {e}")
            return None

    def is_roommate_in_group(self, roommate):
        try:
            with self.db_manager.connect_db() as conn:
                cursor = conn.execute(
                    """
                    SELECT * FROM Pairing WHERE user_id = ? and group_id = ?
                    """,
                    (roommate.id, self.id)
                )
                row = cursor.fetchone()
                cursor.close()
        except sqlite3.Error as e:
            print(f"Error adding roommate to group: {e}")
            return None
        return row is not None

    def is_code_unique(self, code):
        try:
            with self.db_manager.connect_db() as conn:
                cursor = conn.execute("SELECT * FROM RoommateGroups where code = ?", (code,))
                return cursor.fetchone() is None
        except sqlite3.Error as e:
            print(f"Error checking for unique code: {e}")

    # Needed for DatabaseMixin universal get_by_id() method
    @classmethod
    def from_db_row(cls, row):
        group = cls(
            group_name=row[1]
        )
        group.id = row[0]
        group.code = row[2]
        return group

    @classmethod
    def get_by_code(cls, code):
        db_manager = DatabaseManager()
        try:
            with db_manager.connect_db() as conn:
                cursor = conn.execute(
                    """
                    SELECT * FROM RoommateGroups WHERE code = ?
                    """,
                    (code,)
                )
                row = cursor.fetchone()
                cursor.close()
                if row is None:
                    return None
                return cls.from_db_row(row)
        except sqlite3.Error as e:
            print(f"Error fetching group by code: {e}")
            return None
