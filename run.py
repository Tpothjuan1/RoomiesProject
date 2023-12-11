from flask import Flask, render_template, session
from app.blueprints.auth import auth_blueprint
from app.blueprints.events import event_bp
from app.blueprints.group_blueprint import group_blueprint
from app.blueprints.tasks import task_bp
from app.blueprints.tasks import has_been_nudged
from app.classes.database_manager import DatabaseManager
from app.classes.roommate import Roommate
from app.classes.utils import GetUnasTasksGroup, GetUPendingTasks


app = Flask(__name__, template_folder="app/templates")
db_manager = DatabaseManager()

# Needed for sessions
app.secret_key = "some_secret_key"

app.register_blueprint(auth_blueprint)
app.register_blueprint(group_blueprint)
app.register_blueprint(task_bp)
app.register_blueprint(event_bp)


@app.route("/")
def home():
    user_groups = []
    unassignedTasks = []
    userTasks = []
    nudge_count = 0
    if "user_id" in session:
        user_id = session["user_id"]
        roommate = Roommate.get_by_id(user_id)
        if roommate:
            user_groups = roommate.get_groups_of_roommate()

        # Get unassigned tasks for side bar

        if "code" in session:
            unassignedTasks = GetUnasTasksGroup(session["code"], numTasks=3)

        # Get tasks assigned to logged in user for side bar
        userTasks = GetUPendingTasks(session["user_id"], 3)

        # checks if user has been nudged
        nudge_count = has_been_nudged(user_id)

    return render_template(
        "index.html",
        user_groups=user_groups,
        unassignedTasks=unassignedTasks,
        userTasks=userTasks,
        nudge_count=nudge_count,
    )


if __name__ == "__main__":
    db_manager.initialize_db()
    app.run(debug=True)
