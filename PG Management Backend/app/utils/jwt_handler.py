from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    payload = data.copy()

    payload["exp"] = datetime.utcnow() + timedelta(days=1)

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token