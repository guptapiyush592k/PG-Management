from fastapi import APIRouter, HTTPException

from app.models.user_model import (
    UserSignup,
    UserLogin
)

from app.services.auth_service import (
    signup_user,
    login_user
)

router = APIRouter()

@router.post("/signup")
def signup(data: UserSignup):

    try:
        token = signup_user(data)
        print(token)

        return {
            "success": True,
            "token": token
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.post("/login")
def login(data: UserLogin):

    try:
        token = login_user(data)

        return {
            "success": True,
            "token": token
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )