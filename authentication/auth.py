from flask import Blueprint, render_template, request

auth = Blueprint("auth", __name__, static_folder="static", template_folder="templates")
interactor = db.get_interactor("key.json")

@auth.route("/login")
def login():
    return render_template("login.html")

@auth.route("/sign-up")
def signup():
    return render_template("signup.html")

@auth.route("/sign-up/student", methods=["GET", "POST"])
def signupStudent():
    if request.method == "POST":
        pass
    return render_template("signup_student.html")

@auth.route('/sign-up/sponsor', methods=["GET", "POST"])
def signupSponsor():
    if request.method == "POST":
        pass
    return render_template("signup_sponsor.html")

@auth.route('sign-up/admin', methods=["GET", "POST"])
def signupAdmin():
    if request.method == "POST":
        pass
    return render_template("signup_admin.html")