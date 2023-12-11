#####################################################
# Tasks blueprint                                   #
# Author: Juan Sanchez Moreno                       #
#####################################################

################# IMPORTS ###########################

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    abort,
)
from ..classes.task import Task
import sqlite3 as sql
from datetime import datetime
from ..classes.utils import GetUsersInGroup, GetGroupIdFromCode
from app.classes.database_manager import DatabaseManager

db_manager = DatabaseManager()

# Blueprint object
task_bp = Blueprint("task_bp", __name__)


# route to see all tasks assigned to current user
@task_bp.route("/seemytasks")
def Seemytasks():
    # Retreive my tasks from the DB

    # con = sql.connect("Roomies.db")
    con = db_manager.connect_db()

    if not con:
        # maybe return message somewhere with flash?
        print(f"Database connection error.")

    try:
        with db_manager.connect_db() as con:
            # Get row objects from queries
            con.row_factory = sql.Row
            cursor = con.cursor()
            # fetch all tasks assigned to logged in user
            rows = cursor.execute(
                """
            SELECT taskId, description, dueDate, priority
            FROM Task
            WHERE assignedTo = ? AND completed = 0;
            """,
                (session.get("user_id"),),
            ).fetchall()
            cursor.close()
    except sql.Error as e:
        print(f"Database error: {e}")

    # cursor.close()

    # No tasks retreived
    if (len(rows)) == 0:
        flash("You have no tasks assigned to you. Sit back and relax.")

    return render_template("showtasks.html", rows=rows, page="mytasks")


# route to see all tasks assigned to group
@task_bp.route("/seegroupstasks")
def Seetasks():
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
                                WHERE code = ?) AND completed = 0;
                """,
                (session.get("code"),),
            ).fetchall()

            cursor.close()

    except sql.Error as e:
        print(f"Database error: {e}")

    # No tasks retreived
    if (len(rows)) == 0:
        flash("There are no tasks in your group. Sit back and Relax.")

    return render_template("showtasks.html", rows=rows, page="grouptasks")


# route to see all unassigned tasks on a group
@task_bp.route("/seeunassignedtasks")
def SeeUtasks():
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
                                WHERE code = ?) AND completed = 0 AND assignedTo = -1;
                """,
                (session.get("code"),),
            ).fetchall()

            cursor.close()

    except sql.Error as e:
        print(f"Database error: {e}")

    # No tasks retreived
    if (len(rows)) == 0:
        flash("This is a hardworking team. There are no tasks unassiged. Good Job!")

    return render_template("showtasks.html", rows=rows, page="unassignedtasks")


# route to see details on specific task
@task_bp.route("/task/<tnum>")
def task(tnum):
    ## Retrieve task info from db

    # con = sql.connect("Roomies.db")

    con = db_manager.connect_db()

    if not con:
        # maybe return message somewhere with flash?
        print(f"Database connection error.")

    try:
        with db_manager.connect_db() as con:
            # Get row objects from queries
            con.row_factory = sql.Row

            cursor = con.cursor()

            # fetch all tasks assigned to logged in user
            rows = cursor.execute(
                """
                SELECT *
                FROM Task
                WHERE taskId = ?;
                """,
                (tnum,),
            ).fetchone()

            uid = rows["assignedTo"]
            uid2 = rows["createdBy"]

            # Get usernames instead of uids
            username = cursor.execute(
                """
                SELECT username
                FROM Roommates
                WHERE id = ?;
                """,
                (uid,),
            ).fetchone()

            username2 = cursor.execute(
                """
                SELECT username
                FROM Roommates
                WHERE id = ?;
                """,
                (uid2,),
            ).fetchone()

            cursor.close()
    except sql.Error as e:
        print(f"Database error: {e}")
    return render_template("showtask.html", rows=rows, usernames=[username, username2])


# Route to render create_task.html
@task_bp.route("/createtask")
def RenderCreateTask():
    # check if signed in
    if session.get("logged_in"):
        return render_template("createtask.html")

    else:
        abort(404)


# Route to Create a task
@task_bp.route("/addtask", methods=["POST"])
def Addtask():
    if request.method == "POST":
        # Input validation Flag
        flag = True

        # all due dates at 11:59 of due date
        duedate = request.form["duedate"]  # YYYY-MM-DD format
        # Validate user selected a valid date
        if len(duedate) < 1:
            flash("Please Select a Date")
            flag = False
            # Select far away date
            duedate = "9999-01-01"

        duedate = duedate + " 23:59"

        priority = int(request.form["priority"])

        description = request.form["description"]
        # Validate description is not empty
        if len(description) < 1:
            flash("Description Can't be empty")
            flag = False

        today = datetime.now().strftime("%Y-%m-%d %H:%M")
        createdby = int(session.get("user_id"))

        # assignedTo
        assignedto = request.form["assignto"]

        # assigned to self
        if assignedto == "myself":
            assignedto = session.get("user_id")
            accepted = 1

        # unassigned. All unassigned tasks will have -1 as user id
        elif assignedto == "unassigned":
            assignedto = -1
            accepted = 0

        # Invited a roommate to complete
        elif assignedto == "invite":
            invited = request.form["invited"]
            usersInGroupDict = dict(GetUsersInGroup(int(session.get("user_id"))))
            assignedto = int(usersInGroupDict[invited])
            accepted = 0

        # group current group
        groupcode = session.get("code")
        groupId = GetGroupIdFromCode(groupcode)

        # Create task object

        newTask = Task(
            assignedto,
            duedate,
            today,
            priority,
            createdby,
            description,
            groupId,
            accepted,
        )

        # Validate that task's due date is not prior to today
        if newTask.Breached():
            flash("Due Date Can't be before today")
            flag = False

        # Only store task if validation passed

        if flag:
            result = newTask.Store()
            if result:
                flash("Task Successfully Added")
            else:
                flash("Task couldn't be added")

        else:
            flash("Task couldn't be added")

        return render_template("createtask.html")


# Route to handle dynamic sublist to invite roomates to do a task
@task_bp.route("/getroomates", methods=["GET"])
def Getroomies():
    assignto = request.args.get("assignto")

    outlist = []

    # assigned to self
    if assignto == "myself":
        outlist = [session.get("username")]

    # unassigned.
    elif assignto == "unassigned":
        outlist = ["Nobody"]

    elif assignto == "invite":
        usersingroup = GetUsersInGroup(int(session.get("user_id")))
        outlist = [row[0] for row in usersingroup]
        if len(outlist) < 1:
            outlist = ["Nobody"]

    return render_template("subselectusers.html", outlist=outlist)


# route to mark a task as completed
@task_bp.route("/completetask/<tid>")
def CompleteTask(tid):
    try:
        with db_manager.connect_db() as con:
            cursor = con.cursor()

            # Mark task as completed
            cursor.execute(
                """
                UPDATE Task
                SET completed = 1
                WHERE taskId = ?;
                """,
                (tid,),
            )

            cursor.close()
        flash("Good work! your Roomies thank you for completing your task")
    except sql.Error as e:
        print(f"Database error: {e}")
    return redirect("/task/{}".format(tid))


@task_bp.route("/completetask/table/<tid>", methods=["GET", "POST"])
def CompleteTaskTable(tid):
    try:
        with db_manager.connect_db() as con:
            cursor = con.cursor()

            # Mark task as completed
            cursor.execute(
                """
                UPDATE Task
                SET completed = 1
                WHERE taskId = ?;
                """,
                (tid,),
            )

            cursor.close()
        flash("Good work! your Roomies thank you for completing your task")
    except sql.Error as e:
        print(f"Database error: {e}")
    return redirect("/seemytasks")


# route to accept a task
@task_bp.route("/accepttask/<tid>", methods=["GET", "POST"])
def AcceptTask(tid):
    try:
        with db_manager.connect_db() as con:
            cursor = con.cursor()

            # Mark task as completed
            cursor.execute(
                """
                UPDATE Task
                SET accepted = 1,
                assignedTo = ?
                WHERE taskId = ?;
                """,
                (
                    session["user_id"],
                    tid,
                ),
            )

            cursor.close()
        flash("You have accepted this task, your Roomies appreaciate your commitment")
    except sql.Error as e:
        print(f"Database error: {e}")
    return redirect("/task/{}".format(tid))

@task_bp.route("/accepttask/table/<tid>", methods=["GET", "POST"])
def AcceptTaskTable(tid):
    try:
        with db_manager.connect_db() as con:
            cursor = con.cursor()

            # Mark task as completed
            cursor.execute(
                """
                UPDATE Task
                SET accepted = 1,
                assignedTo = ?
                WHERE taskId = ?;
                """,
                (
                    session["user_id"],
                    tid,
                ),
            )

            cursor.close()
        flash("You have accepted this task, your Roomies appreaciate your commitment")
    except sql.Error as e:
        print(f"Database error: {e}")
    return redirect("/seeunassignedtasks")


# route to reject a task
@task_bp.route("/rejecttask/<tid>")
def RejectTask(tid):
    try:
        with db_manager.connect_db() as con:
            cursor = con.cursor()

            # Mark task as completed
            cursor.execute(
                """
                UPDATE Task
                SET accepted = 0,
                assignedTo = -1
                WHERE taskId = ?;
                """,
                (tid,),
            )

            cursor.close()
        flash("This is now an orphan task")
        flash("We understand sometimes there is too much going on in your life")
    except sql.Error as e:
        print(f"Database error: {e}")
    return redirect("/task/{}".format(tid))


# route to change a task's priority for nudging
@task_bp.route("/changepnudge/<tid>", methods=["POST"])
def ChangeNudge(tid):
    try:
        # Extract the form data using request.form
        priority = 0

        with db_manager.connect_db() as con:
            cursor = con.cursor()

            # Update the priority of the task
            cursor.execute(
                """
                UPDATE Task
                SET priority = ?
                WHERE taskId = ?;
                """,
                (priority, tid),
            )

            cursor.close()
    except sql.Error as e:
        print(f"Database error: {e}")

    return redirect("/seegroupstasks")  # return back to task page

# snooze a nudged task
@task_bp.route("/snooze/<tid>", methods=["POST", "GET"])
def Snooze(tid):
    try:
        # Extract the form data using request.form
        priority = 1

        with db_manager.connect_db() as con:
            cursor = con.cursor()

            # Update the priority of the task
            cursor.execute(
                """
                UPDATE Task
                SET priority = ?
                WHERE taskId = ?;
                """,
                (priority, tid),
            )

            cursor.close()
    except sql.Error as e:
        print(f"Database error: {e}")

    flash("You have snoozed the nudge, please complete the task as soon as possible")

    return redirect("/seemytasks")

# function to check if a user has been nudged
def has_been_nudged(user_id):
    try:
        with db_manager.connect_db() as con:
            cursor = con.cursor()

            # Check if the user has tasks with priority 0
            count = cursor.execute(
                """
                SELECT COUNT(*)
                FROM Task
                WHERE assignedTo = ? AND priority = 0 AND completed = 0;
                """,
                (user_id,),
            ).fetchone()[0]

            cursor.close()

            return count
    except sql.Error as e:
        print(f"Database error: {e}")
        return 0  # Return 0 in case of an error
