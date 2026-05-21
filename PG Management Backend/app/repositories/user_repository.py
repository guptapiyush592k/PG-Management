from app.utils.file_handler import read_users, write_users

def get_user_by_email(email: str):
    users = read_users()

    for user in users:
        if user["email"] == email:
            return user

    return None

def create_user(user_data: dict):
    users = read_users()

    users.append(user_data)

    write_users(users)