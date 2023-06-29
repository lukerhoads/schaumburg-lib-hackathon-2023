from flask import request

def get_user():
    userId = request.cookies.get('userIDD')
    if userId and userId != "":
        split = userId.split(" ")
        return int(split[1]), split[0]
    return None, ""