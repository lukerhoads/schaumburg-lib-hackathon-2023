from flask import Flask, render_template, url_for, redirect, request
from authentication.auth import auth
from firebase_admin import credentials, firestore, initialize_app
from db import Collection, DatabaseInteractor, get_interactor

app = Flask(__name__)
app.register_blueprint(auth, url_prefix="/auth")

interactor = get_interactor()

@app.route('/')
def index():
    # Get logged in user
    user = None 
    # If no user, redirect to login
    if not user:
        return redirect("/auth/login")
    
    # Get homepage data
    # - User name
    # - Clubs the user belongs to
    data = {}
    data["clubs"] = interactor.get_clubs_by_school_id(user["school"])
    return render_template("index.html", data=data)

@app.route('/<clubId>', methods=["GET", "POST"])
def clubPage(clubId):
    if request.method == "POST":
        # Post creation
        pass
    # Get club ID from database
    data = {}
    data["posts"] = interactor.posts_by_club_id(clubId)
    data["club"] = interactor.get_collection('clubs').read(clubId)
    data["userInClub"] = False
    return render_template("club.html", data=data)

@app.route('/admin/', methods=["GET", "POST"])
def admin():
    return render_template('admin_panel.html')

if __name__ == '__main__':
    app.run(debug=True)
