from flask import Blueprint, request, make_response, redirect, render_template, request
from db import get_interactor 
from firebase_admin import credentials, firestore, initialize_app
from utils import get_user

# cred = credentials.Certificate("key.json")
# dbapp = initialize_app(cred)

auth = Blueprint("auth", __name__, static_folder="static", template_folder="templates")
interactor = get_interactor()

@auth.route("/login")
def login():
    user_id, user_type = get_user()
    if user_id != None:
        return redirect("/")
    return render_template("login.html")

@auth.route("/sign-up")
def signup():
    user_id, user_type = get_user()
    if user_id != None:
        return redirect("/")    
    return render_template("signup.html")

@auth.route("/sign-up/student", methods=["GET", "POST"])
def signupStudent():
    user_id, user_type = get_user()
    if user_id != None:
        return redirect("/")    
    if request.method == "POST":
        # Create user 
        # Send cookie back
        # Redirect
        name = request.form.get("name")
        email = request.form.get("email")
        school = request.form.get("school")
        id = interactor.create_student(schoolId=school, name=name, email=email)
        resp = make_response(redirect("/"))
        cookie_val = "student " + str(id)
        resp.set_cookie('userIDD', cookie_val)
        return resp
    return render_template("signup_student.html")

@auth.route('/sign-up/sponsor', methods=["GET", "POST"])
def signupSponsor():
    user_id, user_type = get_user()
    if user_id != None:
        return redirect("/")    
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        school = request.form.get("school")
        tags = request.form.get("tags")
        id = interactor.crea(schoolId=school, name=name, email=email)
        resp = make_response(redirect("/"))
        cookie_val = "sponsor " + str(id)
        resp.set_cookie('userIDD', cookie_val)
        return resp
        pass
    return render_template("signup_sponsor.html")

@auth.route('sign-up/admin', methods=["GET", "POST"])
def signupAdmin():
    user_id, user_type = get_user()
    if user_id != None:
        return redirect("/")
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        school = request.form.get("school")
        id = interactor.create_student(schoolId=school, name=name, email=email)
        resp = make_response(redirect("/"))
        cookie_val = "admin " + str(id)
        resp.set_cookie('userIDD', cookie_val)
        return resp
        pass
    return render_template("signup_admin.html")