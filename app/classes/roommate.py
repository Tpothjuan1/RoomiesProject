import sqlite3
from flask_bcrypt import Bcrypt
from .database_manager import DatabaseManager, DatabaseMixin
from .group import Group


class Roommate(DatabaseMixin):
    TABLE_NAME = "Roommates"

    def __init__(self, username, email, password, code=None):
        self.username = username
        self.email = email
        self.code = code
        self.id = None
        self.db_manager = DatabaseManager()
        self.bcrypt = Bcrypt()
        self.password = password

    # Creating and updating Users
    def save_to_db(self):
        try:
            with self.db_manager.connect_db() as conn:
                if self.id is None:
                    # Save to database and return user ID
                    cursor = conn.execute(
                        """
                        INSERT INTO Roommates (username, email, password, code)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            self.username,
                            self.email,
                            self.bcrypt.generate_password_hash(self.password).decode(
                                "utf-8"
                            ),
                            self.code,
                        ),
                    )
                    conn.commit()
                    self.id = cursor.lastrowid
                else:
                    conn.execute(
                        """
                        UPDATE Roommates
                        SET username = ?, email = ?, password = ?, code = ?
                        WHERE id = ?
                        """,
                        (self.username, self.email, self.password, self.code, self.id),
                    )
                    conn.commit()
            cursor.close()
        except sqlite3.Error as e:
            print(f"Error saving user: {e}")
            return None

    def join_group_from_code(self, code):
        group = Group.get_by_code(code)
        return group.add_roommate(self)

    def join_group(self, group):
        return group.add_roommate(self)

    def leave_group(self, group):
        return group.remove_roommate(self)

    def get_groups_of_roommate(self):
        groups = []
        try:
            with self.db_manager.connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT RoommateGroups.*
                    FROM Pairing
                    LEFT JOIN RoommateGroups ON Pairing.group_id = RoommateGroups.id
                    WHERE Pairing.user_id = ?
                    """,
                    (self.id,),
                )
                rows = cursor.fetchall()
                for row in rows:
                    print(row)
                    groups.append(Group.from_db_row(row))
        except sqlite3.Error as e:
            print(f"Error fetching groups: {e}")
        return groups

    @classmethod
    def get_by_email_or_username(cls, name):
        db_manager = DatabaseManager()
        try:
            with db_manager.connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM Roommates WHERE username = ? or email = ?",
                    (name, name),
                )
                row = cursor.fetchone()
                cursor.close()
                if row is None:
                    return None
            return Roommate.from_db_row(row)
        except sqlite3.Error as e:
            print(f"Error finding user: {e}")
            return None

    @staticmethod
    def are_credentials_unique(username, email):
        return (
            Roommate.get_by_email_or_username(username) is None
            and Roommate.get_by_email_or_username(email) is None
        )

    @staticmethod
    def check_pwd_hash(hashed_password, password):
        return Bcrypt().check_password_hash(hashed_password, password)

    # Needed for DatabaseMixin universal get_by_id() method

    @classmethod
    def from_db_row(cls, row):
        roommate = cls(username=row[1], email=row[2], password=row[3], code=row[4])
        roommate.id = row[0]
        return roommate
