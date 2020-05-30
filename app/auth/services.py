from injector import inject
from werkzeug.security import generate_password_hash

from app.database.db import db
from app.database.models import User, Profile
from app.database.repositories import UserRepo, ProfileRepo


class UserRegistration:

    @inject
    def __init__(self, user_repo: UserRepo, profile_repo: ProfileRepo):
        self.user_repo = user_repo
        self.profile_repo = profile_repo
        self.db = db

    def register(self, **kwargs):
        user = User(email=kwargs['email'], password=generate_password_hash(kwargs['password']))
        self.user_repo.save(user)
        profile = Profile(
            first_name=kwargs['first_name'], last_name=kwargs['last_name'],
            interests=kwargs['interests'], birth_date=kwargs['birth_date'], gender=kwargs['gender'],
            city_id=kwargs['city_id'], user_id=user.id
        )
        self.profile_repo.save(profile)
        self.db.commit()
        user.profile = profile
        return user
