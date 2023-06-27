from flask import Flask, render_template, url_for, redirect
from authentication.auth import auth
from firebase_admin import credentials, firestore, initialize_app
from db import Collection

app = Flask(__name__)
app.register_blueprint(auth, url_prefix="/auth")

cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
school_collection = Collection(db, 'school')

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
    return render_template("index.html", data=data)

@app.route('/<clubId>')
def clubPage(clubId):
    # Get club ID from database
    data = {}
    return render_template("club.html", data=data)

if __name__ == '__main__':
    app.run(debug=True)
