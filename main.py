from flask import Flask, render_template, make_response, url_for, redirect, request
from authentication.auth import auth
from firebase_admin import credentials, firestore, initialize_app
from db import Collection, DatabaseInteractor, get_interactor
from utils import get_user, create_error_data
from datetime import datetime 

app = Flask(__name__)
app.register_blueprint(auth, url_prefix="/auth")

interactor = get_interactor()

@app.route('/')
def index():
    # Get logged in user
    user_id, user_type = get_user()
    if user_id != None:
        if user_type == "student":
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
        elif user_type == "sponsor":
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
        elif user_type == "admin":
            data = {}
            user = interactor.get_collection('school').read(user_id)
            data["user"] = user
            data["clubs"] = interactor.clubs_by_school_id(user["id"])
            data["type"] = "admin"
            return render_template("index.html", data=data)
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
    if user_id != None:
        name = request.form.get("name")
        tags = request.form.get("tags")
        description = request.form.get("description")
        if user_type == "student":
            id = interactor.create_club(name=name, tags=tags, studentId=user_id, description=description)
        elif user_type == "admin":
            id = interactor.create_club_as_admin(name=name, tags=tags, adminId=user_id, description=description)
        else:
            id = interactor.create_club_as_sponsor(name, tags, adminId)(name=name, tags=tags, sponsorId=user_id, description=description)
        return redirect("/")

        

    return render_template("error.html", data=create_error_data("Error creating club "))

@app.route("/create-club")
def create():
    return render_template("create-club.html")

@app.route('/<clubId>', methods=["GET"])
def clubPage(clubId):
    user_id, user_type = get_user()
    if user_id == None:
        return redirect("/auth/login")

    # Get club ID from database
    data = {}
    postsDb = interactor.posts_by_club_id(clubId)
    newPosts = []
    for post in postsDb:
        newPost = post 
        comments = interactor.get_comments_by_post_id(post["id"])
        newPost["comments"] = len(comments)
        newPosts.append(newPost)
    data["posts"] = newPosts
    club = interactor.get_collection('club').read(clubId)
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
        userInClub = True
    data["userInClub"] = userInClub 
    return render_template("club.html", data=data)

@app.route('/<clubId>/join', methods=["GET"])
def clubJoin(clubId):
    user_id, user_type = get_user()
    if user_id == None:
        return redirect("/auth/login")
    
    if user_type == "student":
        interactor.add_student_to_club(user_id, clubId)
        return redirect("/" + clubId)
    elif user_type == "sponsor":
        club = interactor.get_collection('club').read(clubId)
        if club["administrator"] != None:
            return render_template("error.html", data=create_error_data("Club already has an administrator"))
        interactor.add_sponsor_to_club(clubId, sponsorId)
        return redirect("/" + clubId)

    return render_template("error.html", data=create_error_data("Invalid user type"))

@app.route('/<clubId>/post', methods=["GET", "POST"])
def clubPost(clubId):
    user_id, user_type = get_user()
    if user_id == None:
        return redirect("/auth/login")

    if request.method == "POST":
        authorName = ""
        if user_type == "student":
            student = interactor.get_collection("student").read(user_id)
            authorName = student["name"]
        elif user_type == "sponsor":
            sponsor = interactor.get_collection("sponsor").read(user_id)
            authorName = sponsor["name"]
        else:
            school = interactor.get_collection("school").read(user_id)
            authorName = school["name"]
        content = request.form.get("content")
        title = request.form.get("title")
        if content == None or content == "" or title == None or title == "":
            return render_template("error.html", data=create_error_data("Empty post content or title"))
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        id = interactor.create_post(content, clubId, title, authorName=authorName, date=date_time)
        prevClub = interactor.get_collection('club').read(clubId)
        if prevClub == None:
            return render_template("error.html", data=create_error_data("Could not find club"))
        interactor.get_collection('club').update(clubId, {
            "posts": prevClub["posts"] + 1
        })
        return redirect("/" + clubId)

    data = {}
    data["clubId"] = clubId
    return render_template("create-post.html", data=data)

@app.route('/<clubId>/sponsor', methods=["GET"])
def clubSponsor(clubId):
    # Add sponsor to club, redirects them to login if they do not already have an account
    # After they have logged in, it redirects them to this page again where they are put as the club sponsor
    pass

@app.route('/admin', methods=["GET"])
def admin():
    user_id, user_type = get_user()
    if user_id == None:
        return redirect("/auth/login")

    if user_type != "admin":
        return render_template("error.html", data=create_error_data("Unauthorized"))

    data = {}
    clubs = interactor.clubs_by_school_id(user_id)
    data["clubs"] = clubs
    return render_template('admin_panel.html', data=data)

@app.route('/admin/<clubId>', methods=["GET", "POST"])
def adminEditClub(clubId):
    user_id, user_type = get_user()
    if user_id == None:
        return redirect("/auth/login")

    if user_type != "admin":
        return render_template("error.html", data=create_error_data("Unauthorized"))
    
    currentClub = interactor.get_collection('club').read(clubId)
    if request.method == "POST":
        if currentClub == None:
            return render_template("error.html", data=create_error_data("COuld not find current club"))

        if user_id != None:
            name = request.form.get("name")
            tags = request.form.get("tags")
            description = request.form.get("description")
            interactor.get_collection('club').update(id=currentClub["id"], object={
                "school": currentClub["school"],
                "id": currentClub["id"],
                "name": name,
                "tags": tags,
                "posts": currentClub["posts"],
                "administrator": currentClub["administrator"],
                "students": currentClub["students"],
                "description": description,
            })
            return redirect("/admin")

    data = {}
    data["clubId"] = clubId
    data["name"] = currentClub["name"]
    data["description"] = currentClub["description"]
    tags = currentClub["tags"]
    if len(tags) > 0:
        data["tags"] = currentClub["tags"]
    else:
        data["tags"] = ""
    return render_template("edit-club.html", data=data)

# hello
@app.route('/admin/<clubId>/delete', methods=["GET"])
def deleteClub(clubId):
    user_id, user_type = get_user()
    if user_id == None:
        return redirect("/auth/login")

    if user_type != "admin":
        return render_template("error.html", data=create_error_data("Unauthorized"))
    
    club = interactor.get_collection("club").read(clubId)
    if club == None:
        return render_template("error.html", data=create_error_data("Cannot find club to delete"))

    interactor.get_collection("club").delete(clubId)
    return redirect("/admin")

@app.route('/<clubId>/<postId>', methods=["GET", "POST"])
def post(clubId, postId):
    user_id, user_type = get_user()
    if user_id == None:
        return redirect("/auth/login")

    if request.method == "POST":
        authorName = ""
        if user_type == "student":
            student = interactor.get_collection("student").read(user_id)
            authorName = student["name"]
        elif user_type == "sponsor":
            sponsor = interactor.get_collection("sponsor").read(user_id)
            authorName = sponsor["name"]
        else:
            school = interactor.get_collection("school").read(user_id)
            authorName = school["name"]

        content = request.form.get("reply")
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        interactor.create_comment(postId=postId, authorName=authorName, content=content, timestamp=date_time)
        return redirect('/' + clubId + '/' + postId)

    data = {}
    comments = interactor.get_comments_by_post_id(postId)
    post = interactor.get_collection("post").read(postId)
    if post == None:
        return render_template("error.html", data=create_error_data("Could not find post"))

    data["clubId"] = clubId 
    data["postId"] = postId
    data["comments"] = comments
    data["post"] = post
    return render_template('post.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
