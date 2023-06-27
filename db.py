
# Functions needed:
# - List clubs by school ID
# - List students in club by club ID

class Collection:
    collection = None 

    def __init__(self, db, collection):
        self.collection = db.collection(collection)

    def create(self, object):
        id = 0 
        id = len(self.read())
        self.collection.document(id).set(object)
        return id

    def read(self, id):
        if id:
            school = self.collection.document(id).get()
            return school.to_dict()
        schools = [doc.to_dict() for doc in self.collection.stream()]
        return schools
        
