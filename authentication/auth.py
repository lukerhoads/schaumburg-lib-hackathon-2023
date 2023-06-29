from flask import Blueprint, request, make_response, redirect, render_template, request
from db import get_interactor 
from firebase_admin import credentials, firestore, initialize_app
from utils import get_user, create_error_data

# cred = credentials.Certificate("key.json")
# dbapp = initialize_app(cred)

auth = Blueprint("auth", __name__, static_folder="static", template_folder="templates")
interactor = get_interactor()

@auth.route("/login", methods=["GET", "POST"])
def login():
    user_id, user_type = get_user()
    if user_id != None:
        return redirect("/")

    if request.method == "POST":
        email = request.form.get("email")
        student = interactor.get_student_by_email(email)
        sponsor = interactor.get_sponsor_by_email(email)
        admin = interactor.get_admin_by_email(email)
        print("Ele: ", student, sponsor, admin)

        if student != None:
            resp = make_response(redirect("/"))
            cookie_val = "student " + str(student["id"])
            resp.set_cookie('userIDD', cookie_val)
            return resp
        elif sponsor != None:
            resp = make_response(redirect("/"))
            cookie_val = "sponsor " + str(sponsor["id"])
            resp.set_cookie('userIDD', cookie_val)
            return resp
        elif admin != None:
            resp = make_response(redirect("/"))
            cookie_val = "admin " + str(school["id"])
            resp.set_cookie('userIDD', cookie_val)
            return resp

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
        email_ending = "@" + email.split("@")[1]
        school = interactor.get_school_by_email_ending(email_ending) # Remove need to specify school
        # Pickup school from email suffix automatically
        if school == None:
            return render_template("error.html", data=create_error_data("Unable to find school with that name"))
        id = interactor.create_student(schoolId=school["id"], name=name, email=email)
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
        if interactor.get_school_by_name(school) == None:
            return render_template("error.html", data=create_error_data("Unable to find school with that name"))
        tags = request.form.get("tags")
        id = interactor.create_sponsor(schoolId=school, name=name, email=email)
        resp = make_response(redirect("/"))
        cookie_val = "sponsor " + str(id)
        resp.set_cookie('userIDD', cookie_val)
        return resp

    return render_template("signup_sponsor.html")

@auth.route('sign-up/admin', methods=["GET", "POST"])
def signupAdmin():
    user_id, user_type = get_user()
    if user_id != None:
        return redirect("/")
    if request.method == "POST":
        email = request.form.get("email")
        school = request.form.get("school")
        domain = request.form.get("domain")
        id = interactor.create_school(name=school, adminEmail=email, emailSuffixes=domain)
        resp = make_response(redirect("/admin"))
        cookie_val = "admin " + str(id)
        resp.set_cookie('userIDD', cookie_val)
        return resp

    return render_template("signup_admin.html")