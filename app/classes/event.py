#####################################################
# event class file.                                 #
# Author: Juan Sanchez Moreno                       #
#####################################################

################# IMPORTS ###########################

from datetime import datetime
import sqlite3 as sql


################ CLASS  #############################


class Event:
    # Constructor
    # Date inputs are strings in the format "%Y-%m-%d %H:%M"
    def __init__(self, date, dateCreated, createdBy, description, groupId, id=None):
        self.timeformat = "%Y-%m-%d %H:%M"
        self.date = datetime.strptime(date, self.timeformat)
        self.dateCreated = datetime.strptime(dateCreated, self.timeformat)
        self.createdBy = createdBy
        self.description = description
        self.groupId = groupId
        self.id = id

    # Get remaining time form now until event is due return days, hours and minutes in integer
    def GetTimeRemaining(self):
        remainingTime = self.date - datetime.now()
        totalSeconds = remainingTime.total_seconds()
        days = totalSeconds // 86400
        hours = (totalSeconds % 86400) // 3600
        minutes = (totalSeconds % 3600) // 60

        return int(days), int(hours), int(minutes)

    # Mutator method for due date attribute
    # Date inputs are strings in the format "%Y-%m-%d %H:%M"
    def ChangeDueDate(self, newdate):
        self.date = datetime.strptime(newdate, self.timeformat)

    def Store(self):
        # if any of the not null attributes is none don't store
        if (
            self.groupId == None
            or self.date == None
            or self.dateCreated == None
            or self.createdBy == None
            or self.description == None
        ):
            return False

        # Case of no event id
        if self.id == None:
            try:
                self.conn = sql.connect("./Roomies.db")
                self.cur = self.conn.cursor()

                # Check if table name exists

                self.cur.execute(
                    """
                    INSERT INTO Event (date, dateCreated, createdBy, description, groupId)
                    VALUES (?,?,?,?,?);
                    """,
                    (
                        self.date.strftime(self.timeformat),
                        self.dateCreated.strftime(self.timeformat),
                        self.createdBy,
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
                    INSERT INTO Event (eventId,date, dateCreated, createdBy, description, groupId)
                    VALUES (?,?,?,?,?,?);
                    """,
                    (
                        self.id,
                        self.date.strftime(self.timeformat),
                        self.dateCreated.strftime(self.timeformat),
                        self.createdBy,
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
