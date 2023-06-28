from flask import Flask, render_template, url_for, redirect
from authentication.auth import auth
from firebase_admin import credentials, firestore, initialize_app
from db import Collection, DatabaseInteractor

# Functions needed:
# - List clubs by school ID
# - List students in club by club ID
# - Add student to a club
# - Add administrator to a club
# - Add a club with a school id
def get_interactor(cred_path):
    cred = credentials.Certificate(cred_path)
    default_app = None 
    if not _apps:
        default_app = initialize_app(cred)
    else:
        default_app = get_app()

    db = firestore.Client()
    interactor = DatabaseInteractor(db)
    return interactor

class Collection:
    collection = None 

    def __init__(self, db, collection):
        self.collection = db.collection(collection)

    def create(self, object):
        id = len(self.read(None))
        self.collection.document(str(id)).set(object)
        return id
    
    def update(self, id, object):
        self.collection.document(str(id)).update(object)

    def read(self, id):
        if id != None:
            item = self.collection.document(str(id)).get()
            return item.to_dict()
        items = [doc.to_dict() for doc in self.collection.stream()]
        return items
        
class DatabaseInteractor:
    def __init__(self, db):
        pass 
        self.school_collection = Collection(db, 'school') 
        self.student_collection = Collection(db, 'student') 
        self.club_collection = Collection(db, 'club') 
        self.post_collection = Collection(db, 'post') 
        self.sponsor_collection = Collection(db, 'sponsor')

    def get_collection(self, collection):
        mapper = {
            'school': self.school_collection,
            'student': self.student_collection,
            'clubs': self.club_collection,
            'post': self.post_collection,
            'sponsor': self.sponsor_collection,
        }

        return mapper.get(collection)

    def create_school(self, name, emailSuffixes, adminEmail):
        # Check that school does not already exist
        schools = self.school_collection.read()
        for school in schools:
            if school["name"] == name:
                raise ValueError("School with that name already exists")

        # Create school and return ID
        id = self.school_collection.create({
            "name": name,
            "emailSuffixes": emailSuffixes,
            "adminEmail": adminEmail
        })

        return id

    def create_student(self, schoolId, name, email):
        # Check that school does not already exist
        students = self.student_collection.read()
        for student in students:
            if student["name"] == name:
                raise ValueError("Student with that name already exists")

        # Create student and return ID
        id = self.student_collection.create({
            "name": name,
            "email": email,
            "school": schoolId,
            "clubs": []
        })

        return id

    def create_club(self, name, tags, studentId):
        student = self.student_collection.read(studentId)

        # Check that school does not already exist
        clubs = self.school_collection.read()
        for club in clubs:
            if club["name"] == name and club["school"] == student["school"]:
                raise ValueError("Club with that name at that school already exists")

        print("student: ", student)
        id = self.club_collection.create({
            "school": student["school"],
            "name": name,
            "tags": tags,
            "posts": [],
            "administrator": None,
            "students": [studentId]
        })

        return id

    def create_post(self, content, clubId)
    
    def add_student_to_club(self, studentId, clubId):
        prevStudent = self.student_collection.read(studentId)
        prevStudent["clubs"].append(clubId)
        self.student_collection.update(studentId, {
            "clubs": prevStudent["clubs"]
        })

        prevClub = self.club_collection.read(clubId)
        prevClub["students"].append(studentId)
        self.club_collection.update(clubId, {
            "students": prevClub["students"]
        })

    def add_sponsor_to_club(self, clubId, sponsorId):
        self.club_collection.update(clubId, {
            "sponsor": sponsorId,
        })

    def clubs_by_school_id(self, schoolId):
        clubs = self.club_collection.read(None)
        return [club for club in clubs if club.school == schoolId]

    def posts_by_club_id(self, clubId):
        posts = self.post_collection.read()
        postArr = []
        for post in posts:
            if post["club"] == clubId:
                postArr = append(postArr, post)
            
        return postArr