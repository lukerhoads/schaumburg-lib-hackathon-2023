from flask import Flask, render_template, make_response, url_for, redirect, request
from authentication.auth import auth
from firebase_admin import credentials, firestore, initialize_app
from db import Collection, DatabaseInteractor, get_interactor
from utils import get_user, create_error_data

app = Flask(__name__)
app.register_blueprint(auth, url_prefix="/auth")

interactor = get_interactor()

@app.route('/')
def index():
    # Get logged in user
    user_id, user_type = get_user()
    if user_id != None:
        match user_type:
            case "student":
                user = interactor.get_collection('student').read(user_id)
                if user == None:
                    return render_template("error.html", create_error_data("Could not find user by id"))
                data = {}
                data["type"] = "student"
                print("School: ", user["school"])
                school = interactor.get_collection("school").read(user["school"])
                data["schoolName"] = school["name"]
                data["user"] = user
                data["clubs"] = interactor.clubs_by_school_id(user["school"])
                return render_template("index.html", data=data)
            case "sponsor":
                user = interactor.get_collection('sponsor').read(user_id)
                if user == None:
                    return render_template("error.html", create_error_data("Could not find user by id"))
                data = {}
                data["type"] = "sponsor"
                data["user"] = user
                clubs = []
                for club in user["clubs"]:
                    dbClub = interactor.get_collection("club").read(club)
                    clubs.append(dbClub)
                data["clubs"] = clubs
                return render_template("index.html", data=data)
            case "admin":
                return redirect("/admin")
                # admin panel url: /admin

    # If no user, redirect to login
    return redirect("/auth/login")
    
    # Get homepage data
    # - User name
    # - Clubs the user belongs to
    

@app.route('/error')
def error():
    return render_template("error.html")

@app.route('/club', methods=["POST"])
def club():
    user_id, user_type = get_user()
    if user_id != None and user_type == "student":
        name = request.form.get("name")
        tags = request.form.get("tags")
        id = interactor.create_club(name=name, tags=tags, studentId=user_id)
        return redirect("/")

    return redirect("/error")

@app.route("/create")
def create():
    return render_template("create.html")

@app.route('/<clubId>', methods=["GET"])
def clubPage(clubId):
    user_id, user_type = get_user()
    if user_id == None:
        return redirect("/auth/login")

    # Get club ID from database
    data = {}
    data["posts"] = interactor.posts_by_club_id(clubId)
    club = interactor.get_collection('club').read(clubId)
    print("Club: ", club)
    if club == None:
        return render_template("error.html", data=create_error_data("Could not find club"))
    data["club"] = club
    school = interactor.get_collection('school').read(club["school"])
    data["clubSchoolName"] = school["name"]
    userInClub = False
    if user_type == "student":
        student = interactor.get_collection("student").read(user_id)
        for club in student["clubs"]:
            if club == clubId:
                userInClub = True
    elif user_type == "sponsor":
        sponsor = interactor.get_collection("sponsor").read(user_id)
        for club in sponsor["clubs"]:
            if club == clubId:
                userInClub = True
    else:
        return render_template("error.html", data=create_error_data("Invalid user type"))
    data["userInClub"] = userInClub 
    return render_template("club.html", data=data)

@app.route('/<clubId>/join', methods=["POST"])
def clubJoin(clubId):
    user_id, user_type = get_user()
    if user_id == None:
        return redirect("/auth/login")
    
    if user_type == "student":
        interactor.add_student_to_club(studentId, clubId)
    elif user_type == "sponsor":
        interactor.add_sponsor_to_club(clubId, sponsorId)

    return redirect("/error", data=create_error_data("Invalid user type"))

@app.route('/<clubId>/post', methods=["POST"])
def clubPost(clubId):
    content = request.form.get("content")
    interactor.create_post(content, clubId)
    return redirect("/" + clubId)

@app.route('/<clubId>/sponsor', methods=["GET"])
def clubSponsor(clubId):
    # Add sponsor to club, redirects them to login if they do not already have an account
    # After they have logged in, it redirects them to this page again where they are put as the club sponsor
    pass

@app.route('/logout')
def logout():
    resp = make_response(redirect("/"))
    resp.set_cookie('userIDD', "")
    return resp
@app.route('/admin', methods=["GET"])
def admin():
    return render_template('admin_panel.html')

if __name__ == '__main__':
    app.run(debug=True)
