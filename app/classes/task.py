#####################################################
# Task class file.                                  #
# Author: Juan Sanchez Moreno                       #
#####################################################

################# IMPORTS ###########################

from datetime import datetime
import sqlite3 as sql
from .event import Event

################ CLASS  #############################


class Task(Event):
    # Constructor (Missing input validation)
    # Date inputs are strings in the format "%Y-%m-%d %H:%M"
    def __init__(
        self,
        assignedTo,
        dueDate,
        dateCreated,
        priority,
        createdBy,
        description,
        groupId,
        accepted=0,
        taskId=None,
        # will store 0 for pending and 1 for completed
        completed=0,
    ):
        super().__init__(dueDate, dateCreated, createdBy, description, groupId, taskId)
        self.timeformat = "%Y-%m-%d %H:%M"
        self.priority = priority
        self.completed = completed
        self.assignedTo = assignedTo
        self.accepted = accepted

    # If the task due date passed return true
    def Breached(self):
        if (self.date - datetime.now()).total_seconds() < 0:
            return True
        else:
            return False

    # Mutator method to assign task to another user.
    def AssignTo(self, userid):
        self.assignedTo = userid

    # Mutator method for priority attribute input is an integer from 1 to 3 inclusive
    def ChangePriority(self, newpri):
        self.priority = newpri

    # mark task as complete
    def MarkComplete(self):
        self.completed = 1

    # mark task as accepted
    def AcceptTask(self):
        self.accepted = 1

    # method to store a task object to the database
    def Store(self):
        # if any of the not null attributes is none don't store
        if (
            self.assignedTo == None
            or self.date == None
            or self.dateCreated == None
            or self.priority == None
            or self.createdBy == None
            or self.completed == None
            or self.description == None
        ):
            return False

        # Case of no task id
        if self.id == None:
            try:
                self.conn = sql.connect("./Roomies.db")
                self.cur = self.conn.cursor()

                # Check if table name exists

                self.cur.execute(
                    """
                    INSERT INTO Task (assignedTo, dueDate, dateCreated, priority, createdBy, completed, accepted, description,groupId)
                    VALUES (?,?,?,?,?,?,?,?,?);
                    """,
                    (
                        self.assignedTo,
                        self.date.strftime(self.timeformat),
                        self.dateCreated.strftime(self.timeformat),
                        self.priority,
                        self.createdBy,
                        self.completed,
                        self.accepted,
                        self.description,
                        self.groupId,
                    ),
                )

                self.conn.commit()
                self.cur.close()
                self.conn.close()

                return True

            except:
                print("Failed to connect to DB or failed to add task")
                return False

        # Case of not null taskid
        else:
            try:
                self.conn = sql.connect("./Roomies.db")
                self.cur = self.conn.cursor()

                # Check if table name exists

                self.cur.execute(
                    """
                    INSERT INTO Task (taskId, assignedTo, dueDate, dateCreated, priority, createdBy, completed, accepted, description, groupId)
                    VALUES (?,?,?,?,?,?,?,?,?,?);
                    """,
                    (
                        self.id,
                        self.assignedTo,
                        self.date.strftime(self.timeformat),
                        self.dateCreated.strftime(self.timeformat),
                        self.priority,
                        self.createdBy,
                        self.completed,
                        self.accepted,
                        self.description,
                        self.groupId,
                    ),
                )

                self.cur.close()
                self.conn.close()

                return True

            except:
                print("Failed to connect to DB or failed to add task")
                return False
