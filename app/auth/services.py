from flask_login import logout_user, login_user
from injector import inject
from werkzeug.security import generate_password_hash, check_password_hash

from app.auth.exceptions import LoginException
from app.database.db import db, transactional
from app.database.models import User, Profile
from app.database.repositories import UserRepo, ProfileRepo


class UserRegistration:

    @inject
    def __init__(self, user_repo: UserRepo, profile_repo: ProfileRepo):
        self.user_repo = user_repo
        self.profile_repo = profile_repo
        self.db = db

    @transactional
    def register(self, **kwargs):
        user = self.user_repo.save(User(
            email=kwargs['email'], password=generate_password_hash(kwargs['password'])
        ))
        user.profile = self.profile_repo.save(Profile(
            first_name=kwargs['first_name'], last_name=kwargs['last_name'],
            interests=kwargs['interests'], birth_date=kwargs['birth_date'], gender=kwargs['gender'],
            city_id=kwargs['city_id'], user_id=user.id
        ))
        return user


class AuthManager:

    @inject
    def __init__(self, user_repo: UserRepo, profile_repo: ProfileRepo):
        self.user_repo = user_repo
        self.profile_repo = profile_repo

    def login(self, email, password):
        user: User = self.user_repo.find_by_email(email)
        if user is None:
            raise LoginException('E-mail or password incorrect')
        if not check_password_hash(user.password, password):
            raise LoginException('E-mail or password incorrect')
        user.profile = self.profile_repo.find_by_user_id(user.id)
        self.login_user(user)

    def login_user(self, user):
        login_user(user, remember=True)

    def logout(self):
        logout_user()
