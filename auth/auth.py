from flask import Blueprint, render_template

auth = Blueprint("auth", __name__, static_folder="static", template_folder="templates")

@auth.route("/login")
def login():
    return render_template("login.html")