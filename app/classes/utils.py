#####################################################
# Utils file                                        #                       #
#####################################################

################# IMPORTS ###########################

from datetime import datetime
import sqlite3 as sql
from .database_manager import DatabaseManager


# Function that checks if a table exists within a db
def TableExists(tablename, database):
    try:
        conn = sql.connect(database)
        cur = conn.cursor()

        # Check if table name exists

        out = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
            (tablename,),
        ).fetchall()

        # if table doesn't exist
        if len(out) < 1:
            print("Table with name " + tablename + " doesn't exist")
            return False

        cur.close()
        conn.close()

        return True

    except:
        print("Failed to connect to DB or no table with name " + tablename)
        return False


# function that returns the list of tuples (username, uid) in a group except for 1
def GetUsersInGroup(excludedUid):
    try:
        conn = sql.connect("Roomies.db")
        cur = conn.cursor()

        out = cur.execute(
            """
            SELECT username, user_id
            FROM Roommates INNER JOIN 
                (SELECT user_id 
                FROM Pairing 
                WHERE group_id=(SELECT group_id 
                                FROM Pairing 
                                WHERE user_id=?)) 
            AS inter ON Roommates.id = inter.user_id
            WHERE Roommates.id <> ?;
            """,
            (excludedUid, excludedUid),
        ).fetchall()

        return out

    except:
        print("error fetching users")
        return False


# Function that returns the group id given the group code
def GetGroupIdFromCode(code):
    try:
        conn = sql.connect("Roomies.db")
        cur = conn.cursor()

        out = cur.execute(
            """
            SELECT id
            FROM RoommateGroups
            WHERE code = ?;
            """,
            (code,),
        ).fetchone()

        return out[0]

    except:
        print("error group ID")
        return -1


# Function that returns a maximum number of unassigned tasks within a group
def GetUnasTasksGroup(groupCode, numTasks=9999999):
    db_manager = DatabaseManager()
    try:
        with db_manager.connect_db() as con:
            con.row_factory = sql.Row
            cursor = con.cursor()
            rows = cursor.execute(
                """
                SELECT taskId, description, dueDate, priority
                FROM Task
                WHERE groupId = (SELECT id 
                                FROM RoommateGroups
                                WHERE code = ?) AND completed = 0 and assignedTo = -1
                                ORDER BY dueDate
                                LIMIT ?;
                """,
                (groupCode, numTasks),
            ).fetchall()

            cursor.close()

            return rows

    except sql.Error as e:
        print(f"Database error: {e}")
        return -1


# Function that returns a maxium number of pending tasks assigned to user
def GetUPendingTasks(userId, numTasks=9999999):
    db_manager = DatabaseManager()
    try:
        with db_manager.connect_db() as con:
            con.row_factory = sql.Row
            cursor = con.cursor()
            rows = cursor.execute(
                """
                SELECT taskId, description, dueDate, priority
                FROM Task
                WHERE completed = 0 and assignedTo = ?
                                ORDER BY dueDate
                                LIMIT ?;
                """,
                (userId, numTasks),
            ).fetchall()

            cursor.close()

            return rows

    except sql.Error as e:
        print(f"Database error: {e}")
        return -1
