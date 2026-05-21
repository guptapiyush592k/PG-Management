import uuid

from app.repositories.user_repository import (
    get_user_by_email,
    create_user
)

from app.utils.password_handler import (
    hash_password,
    verify_password
)

from app.utils.jwt_handler import create_access_token

def signup_user(data):

    existing_user = get_user_by_email(data.email)
    if existing_user:
        raise Exception("Email already exists")

    user = {
        "id": str(uuid.uuid4()),
        "name": data.name,
        "email": data.email,
        "password_hash": hash_password(data.password)
    }
    print(user)

    create_user(user)

    token = create_access_token({
        "user_id": user["id"],
        "email": user["email"]
    })

    return token

def login_user(data):

    user = get_user_by_email(data.email)

    if not user:
        raise Exception("Invalid credentials")

    valid_password = verify_password(
        data.password,
        user["password_hash"]
    )

    if not valid_password:
        raise Exception("Invalid credentials")

    token = create_access_token({
        "user_id": user["id"],
        "email": user["email"]
    })

    return token