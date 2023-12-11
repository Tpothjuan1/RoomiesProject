from flask import Blueprint, request, redirect, url_for, session
from app.classes.roommate import Roommate
from app.classes.group import Group

group_blueprint = Blueprint("group", __name__)


@group_blueprint.route("/join_group", methods=["POST"])
def join_group():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    group_code = request.form["group_code"]
    group = Group.get_by_code(group_code)
    if group is None:
        return "No group found", 400

    roommate = Roommate.get_by_id(session["user_id"])

    is_roommate_already_in_group = group.is_roommate_in_group(roommate)
    # If they are already in the group, do nothing
    if is_roommate_already_in_group:
        return redirect(url_for("home"))

    if roommate is None:
        return "No user found", 400

    roommate.join_group(group)
    session["code"] = group_code

    return redirect(url_for("home"))


@group_blueprint.route("/create_group", methods=["POST"])
def create_group():
    # Ensure user is logged in
    if "username" not in session:
        return redirect(url_for("auth.login"))

    # Grab fields
    group_name = request.form["group_name"]

    # Create group and save to DB
    newGroup = Group(group_name)
    newGroup.save_to_db()

    session['code'] = newGroup.code
    # Grabbing roommate by stored user id
    roommate = Roommate.get_by_id(session["user_id"])

    if roommate is None:
        return "No user found", 400

    roommate.join_group(newGroup)

    return redirect(url_for("home"))


@group_blueprint.route("/leave-group/<int:group_id>", methods=["POST"])
def leave_group(group_id):
    if "username" not in session:
        return redirect(url_for("auth.login"))

    group = Group.get_by_id(group_id)
    if group is None:
        return "No group found", 400

    roommate = Roommate.get_by_id(session["user_id"])
    if roommate is None:
        return "No user found", 400

    roommate.leave_group(group)
    session['code'] = ''
    return redirect(url_for("home"))
