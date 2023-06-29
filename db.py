from firebase_admin import credentials, firestore, initialize_app, _apps, get_app

initialized = False

# Functions needed:
# - List clubs by school ID
# - List students in club by club ID
# - Add student to a club
# - Add administrator to a club
# - Add a club with a school id
def get_interactor():
    global initialized
    dbapp = None
    if initialized == False:
        cred = credentials.Certificate("key.json")
        dbapp = initialize_app(cred, name="Schaumburg Library Hackathon")
        initialized = True
    else:
        dbapp = get_app(name="Schaumburg Library Hackathon")
    print("before")
    db = firestore.client(dbapp)
    print("after")
    interactor = DatabaseInteractor(db)
    return interactor

class Collection:
    collection = None 

    def __init__(self, db, collection):
        self.collection = db.collection(collection)

    def create(self, object):
        id = len(self.read_all())
        object["id"] = id
        self.collection.document(str(id)).set(object)
        return id
    
    def update(self, id, object):
        self.collection.document(str(id)).update(object)

    def read_all(self):
        items = [doc.to_dict() for doc in self.collection.stream()]
        return items

    def read(self, id):
        item = self.collection.document(str(id)).get()
        return item.to_dict()
        
        
class DatabaseInteractor:
    def __init__(self, db):
        self.school_collection = Collection(db, 'school') 
        self.student_collection = Collection(db, 'student') 
        self.club_collection = Collection(db, 'club') 
        self.post_collection = Collection(db, 'post') 
        self.sponsor_collection = Collection(db, 'sponsor')
        self.comment_collection = Collection(db, 'comment')

    def get_collection(self, collection):
        mapper = {
            'school': self.school_collection,
            'student': self.student_collection,
            'club': self.club_collection,
            'post': self.post_collection,
            'sponsor': self.sponsor_collection,
        }

        return mapper.get(collection)

    def create_comment(self, postId, authorId, content):
        # Create school and return ID
        id = self.comment_collection.create({
            "post": postId,
            "author": authorId,
            "content": content,
        })

        return id

    def create_school(self, name, emailSuffixes, adminEmail):
        # Check that school does not already exist
        schools = self.school_collection.read_all()
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
        students = self.student_collection.read_all()
        for student in students:
            if student["name"] == name:
                raise ValueError("Student with that name already exists")

        # Create student and return ID
        id = self.student_collection.create({
            "name": name,
            "email": email,
            "school": schoolId,
            "clubs": [],
        })

        return id

    def create_sponsor(self, schoolId, name, email, tags):
        # Check that school does not already exist
        sponsors = self.sponsor_collection.read_all()
        for sponsor in sponsors:
            if sponsor["name"] == name:
                raise ValueError("Sponsor with that name already exists")

        # Create student and return ID
        id = self.sponsor_collection.create({
            "name": name,
            "email": email,
            "school": schoolId,
            "tags": [],
            "clubs": []
        })

        return id

    def create_club(self, name, tags, studentId):
        student = self.student_collection.read(studentId)

        # Check that school does not already exist
        clubs = self.school_collection.read_all()
        for club in clubs:
            if club["name"] == name and club["school"] == student["school"]:
                raise ValueError("Club with that name at that school already exists")

        id = self.club_collection.create({
            "school": student["school"],
            "name": name,
            "tags": tags,
            "posts": [],
            "administrator": None,
            "students": [studentId]
        })

        return id

    def create_post(self, content, clubId, title):
        id = self.post_collection.create({
            "content": content,
            "title": title,
            "club": clubId
        })

        return id
    
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
            "administrator": sponsorId,
        })

    def clubs_by_school_id(self, schoolId):
        clubs = self.club_collection.read_all()
        clubResult = []
        for club in clubs:
            if club["school"] == schoolId:
                clubResult.append(club)
            
        return clubResult

    def posts_by_club_id(self, clubId):
        posts = self.post_collection.read_all()
        postArr = []
        for post in posts:
            if post["club"] == clubId:
                postArr.append(post)
            
        return postArr
    
    def get_student_by_email(self, email):
        students = self.student_collection.read_all()
        for student in students:
            if student["email"] == email:
                return student 
        
        return None

    def get_sponsor_by_email(self, email):
        students = self.sponsor_collection.read_all()
        for student in students:
            if student["email"] == email:
                return student 
        
        return None

    def get_school_by_admin_email(self, email):
        students = self.school_collection.read_all()
        for student in students:
            if student["adminEmail"] == email:
                return student 
        
        return None

    def get_school_by_name(self, name):
        students = self.school_collection.read_all()
        for student in students:
            if student["name"] == email:
                return student 
        
        return None

    def get_school_by_email_ending(self, email_ending):
        students = self.school_collection.read_all()
        for student in students:
            emailSuffixes = student["emailSuffixes"]
            for emailSuffix in emailSuffixes:
                if emailSuffix == email_ending:
                    return student 
        
        return None

    def get_comments_by_post_id(self, postId):
        commResult = []
        comments = self.comment_collection.read_all()
        for comment in comments:
            if comment["post"] == postId:
                commResult.append(comment)
        
        return commResult