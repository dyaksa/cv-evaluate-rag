from sqlalchemy.orm import Session
from typing import Optional
from model.model import User
import uuid

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, email: str, password: str) -> Optional[User]:
        try:
            user = User(id=str(uuid.uuid4()), email=email, password=password)
            self.session.add(user)
            self.session.commit()
            return user
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.session.close()

    def find_by_email(self, email: str) -> Optional[User]:
        try:
            return self.session.query(User).filter(User.email == email).first()
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.session.close()
