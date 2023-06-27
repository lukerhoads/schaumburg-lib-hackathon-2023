from flask import Flask, render_template, url_for
from authentication.auth import auth
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)
app.register_blueprint(auth, url_prefix="/auth")

cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()

@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
