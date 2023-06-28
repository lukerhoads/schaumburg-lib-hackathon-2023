from firebase_admin import credentials, firestore, initialize_app
from db import get_interactor

cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db_interactor = get_interactor()

# Random test code
student_id = db_interactor.create_student(schoolId=0, name="HPHS", email="hello@hello.com")
club_id = db_interactor.create_club(name=0, studentId=student_id, tags=["hello", "there"])
student_2_id = db_interactor.create_student(schoolId=0, name="HPHS", email="hello2@hello.com")
db_interactor.add_student_to_club(studentId=student_2_id, clubId=club_id)
