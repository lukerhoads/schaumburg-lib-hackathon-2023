from flask import Flask, render_template, url_for, redirect, request
from authentication.auth import auth
from firebase_admin import credentials, firestore, initialize_app
from db import Collection, DatabaseInteractor, get_interactor
from utils import get_user

app = Flask(__name__)
app.register_blueprint(auth, url_prefix="/auth")

interactor = get_interactor()

@app.route('/')
def index():
    # Get logged in user
    user_id, user_type = get_user()
    if user_id:
        match user_type:
            case "student":
                user = interactor.get_collection('student').read(user_id)
                data = {}
                data["user"] = user
                data["clubs"] = interactor.clubs_by_school_id(user["school"])
                print(data["clubs"])
                return render_template("index.html", data=data)
            case "sponsor":
                pass
            case "admin":
                pass
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
    if user_id and user_type == "student":
        name = request.form.get("name")
        tags = request.form.get("tags")
        id = interactor.create_club(name=name, tags=tags, studentId=user_id)
        return redirect("/")

    return redirect("/error")

@app.route("/create")
def create():
    return render_template("create.html")

@app.route('/<clubId>', methods=["GET", "POST"])
def clubPage(clubId):
    if request.method == "POST":
        # Post creation
        pass
    # Get club ID from database
    data = {}
    data["posts"] = interactor.posts_by_club_id(clubId)
    data["club"] = interactor.get_collection('club').read(clubId)
    data["userInClub"] = False
    return render_template("club.html", data=data)


if __name__ == '__main__':
    app.run(debug=True)
