from helpers import password_utils
from repositories import user_repository
from internal.db import SessionLocal
from flask_jwt_extended import create_access_token

def register(email: str, password: str):
    try:
        user_repo = user_repository.UserRepository(SessionLocal())
        exist_user = user_repo.find_by_email(email.lower())
        if exist_user:
            raise Exception("user already axists")
        
        hashed_password = password_utils.hash_password(password)
        user_repo.create(email=email.lower(), password=hashed_password)

        return True
    except Exception as e:
        raise Exception("errors : ", e)
    
def login(email: str, password: str):
    try:
        user_repo = user_repository.UserRepository(SessionLocal())
        exist_user = user_repo.find_by_email(email.lower())

        if not exist_user:
            raise Exception("user already axists")
        
        verify = password_utils.check_password(password=password, hashed=exist_user.password)

        if not verify:
            raise Exception("password does not match")
        
        token = create_access_token(identity=exist_user.id)
        return token
    except Exception as e:
        raise Exception("errors : ", e)
