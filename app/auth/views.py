from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import logout_user, current_user, login_user

from app.auth.forms import LoginForm, RegistrationForm
from app.auth.services import UserRegistration
from app.database.repositories import CityRepo, UserRepo

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('login', methods=('GET', 'POST'))
def login(user_repo: UserRepo):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = user_repo.find_by_email(form.email.data)
        login_user(user, remember=True)
        return redirect(url_for('main.index'))

    return render_template('auth/login.html', form=form)


@bp.route('logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('register', methods=('GET', 'POST'))
def register(city_repo: CityRepo, user_registration: UserRegistration):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm(request.form)
    form.city.choices = [(city.id, city.name) for city in city_repo.find_all()]
    if request.method == 'POST' and form.validate():
        user = user_registration.register(
            email=form.email.data, password=form.password.data,
            first_name=form.first_name.data, last_name=form.last_name.data,
            interests=form.interests.data, birth_date=form.birth_date.data, gender=form.gender.data,
            city_id=form.city.data,
        )
        login_user(user, remember=True)
        return redirect(url_for('main.profile', profile_id=user.profile.id))

    return render_template('auth/register.html', form=form)
