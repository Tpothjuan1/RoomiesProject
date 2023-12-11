import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from app.classes.group import Group
from app.classes.roommate import Roommate

auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        code = request.form.get("code")

        # Additional input validation needed here

        try:
            # Checking to see if user's credentials are unique
            is_user_unique = Roommate.are_credentials_unique(username, email)

            if not is_user_unique:
                flash("A user with that username or email already exists", "error")
                return redirect(url_for("auth.register"))

            # Creating user, saving to database and logging them in
            new_roommate = Roommate(username, email, password, code)
            new_roommate.save_to_db()

            # Grabbing user that now has an ID and logging them in
            user = Roommate.get_by_id(new_roommate.id)

            if len(code.strip()) != 0:
                g = Group.get_by_code(code)
                if g:
                    g.add_roommate(user)
            else:
                print("No Code!")

            session["user_id"] = user.id
            session["username"] = user.username
            session["code"] = code
            session["logged_in"] = True
            return redirect(url_for("home"))

        except sqlite3.Error:
            return redirect(url_for("auth.register"))

    return render_template("register.html")


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["email"]
        password = request.form["password"]

        user = Roommate.get_by_email_or_username(name)

        # Checking that a user was found with their username/email
        # Also ensuring that their password matches the stored hash using bcrypt
        if user and Roommate.check_pwd_hash(user.password, password):
            groups = user.get_groups_of_roommate()
            session["user_id"] = user.id
            session["username"] = user.username
            session["code"] = '' if len(groups) == 0 else groups[0].code
            session["logged_in"] = True
            # User found
            return redirect(url_for("home"))

        # If we do not return, login failed
        flash("Invalid email or password", "error")

    return render_template("login.html")


@auth_blueprint.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))
