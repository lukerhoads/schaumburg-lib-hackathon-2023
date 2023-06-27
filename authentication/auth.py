from flask import Blueprint, render_template

auth = Blueprint("auth", __name__, static_folder="static", template_folder="templates")

@auth.route("/login")
def login():
    return render_template("login.html")

@auth.route("/sign-up")
def signup():
    return render_template("signup.html")

@auth.route("/sign-up/student")
def signupStudent():
    return render_template("signup_student.html")

@auth.route('/sign-up/sponsor')
def signupSponsor():
    return render_template("signup_sponsor.html")

@auth.route('sign-up/admin')
def signupAdmin():
    return render_template("signup_admin.html")