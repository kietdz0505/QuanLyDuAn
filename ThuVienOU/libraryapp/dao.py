import json

def auth_user(username, password):
    with open("../data/users.json", encoding='utf-8') as f:
        users = json.load(f)
    # Vi du
    for user in users:
        if user['username']==username and user['password']==password:
            return True
    return False