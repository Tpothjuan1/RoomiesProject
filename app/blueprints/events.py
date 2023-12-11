import sqlite3 as sql
from flask import (
    Blueprint,
    request,
    session,
    jsonify
)
from datetime import datetime
from app.classes.database_manager import DatabaseManager

db_manager = DatabaseManager()

event_bp = Blueprint("event_bp", __name__)

# pull events from all groups, and individual tasks into calendar
@event_bp.route('/getevents')
def get_events():
    with db_manager.connect_db() as conn:
        cursor = conn.cursor()

        # get group IDs for the current user
        cursor.execute(
            """
            SELECT RoommateGroups.id
            FROM Pairing
            LEFT JOIN RoommateGroups ON Pairing.group_id = RoommateGroups.id
            WHERE Pairing.user_id = ?
            """,
            (session['user_id'],)
        )
        groups = cursor.fetchall()
        group_ids = [group[0] for group in groups]

        # get events for those groups
        query = "SELECT eventId, dueDate, description FROM Event WHERE groupId IN ({})".format(','.join('?'*len(group_ids)))
        cursor.execute(query, group_ids)
        events = cursor.fetchall()

        task_and_event_list = []
        for event in events:
            event_dict = {
                'id': event[0],
                'title': event[2],
                'start': event[1],
                'color': 'blue',
                'allDay': True
            }
            task_and_event_list.append(event_dict)

        # get individual's tasks
        cursor.execute("SELECT taskId, dueDate, description, priority FROM Task WHERE assignedTo = ? AND completed = 0", (session["user_id"],))
        tasks = cursor.fetchall()

        for task in tasks:
            task_title = f'⭐ {task[2]}' if task[3] == 0 else task[2]
            task_dict = {
                'id': task[0],
                'title': task_title,
                'start': task[1],
                'color': get_color_based_on_priority(task[3]),
                'allDay': True
            }
            task_and_event_list.append(task_dict)

        return jsonify(task_and_event_list)

def get_color_based_on_priority(priority):
    priority_color_map = {
        3: '#cc0000',
        2: '#f2c926',
        1: 'green',
        0: 'purple'
    }
    # default
    return priority_color_map.get(priority, 'gray')

# insert event into database
def insert_event(data):
    connection = sql.connect('Roomies.db')
    cursor = connection.cursor()

    createdBy = session['user_id']

    # get all group IDs for the user
    cursor.execute(
        """
        SELECT group_id
        FROM Pairing
        WHERE user_id = ?
        """,
        (createdBy,)
    )
    groups = cursor.fetchall()

    event_ids = []

    # for each group, insert the event
    for group in groups:
        groupId = group[0]
        query = ''' INSERT INTO Event(dueDate, dateCreated, createdBy, description, groupId)
                    VALUES(?, ?, ?, ?, ?) '''
        values = (data['start'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'), createdBy, data['title'], groupId)

        cursor.execute(query, values)
        event_ids.append(cursor.lastrowid)

    connection.commit()
    connection.close()
    # return a list of events
    return event_ids

# json add event
@event_bp.route('/addevent', methods=['POST'])
def add_event():
    event_data = request.json
    event_id = insert_event(event_data)
    return jsonify({'status': 'success', 'eventId': event_id})
