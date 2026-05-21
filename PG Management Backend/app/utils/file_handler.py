import json

USER_FILE = "app/data/users.json"

def read_users():
    with open(USER_FILE, "r") as file:
        return json.load(file)

def write_users(users):
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=2)