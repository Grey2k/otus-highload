from app import di
from app.database.repositories import ProfileRepo, UserRepo
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(id):
    user_repo: UserRepo = di.get(UserRepo)
    profile_repo = di.get(ProfileRepo)
    user = user_repo.find_by_id(id) if id else None
    if user:
        user.profile = profile_repo.find_by_user_id(user.id)
    return user
