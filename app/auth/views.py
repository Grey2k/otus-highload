from flask import Blueprint, request, render_template, redirect, url_for, make_response
from flask_login import current_user

from app.auth.exceptions import LoginException
from app.auth.forms import LoginForm, RegistrationForm
from app.auth.services import UserRegistration, AuthManager
from app.database.repositories import CityRepo
import app.jwt as jwt

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('login', methods=('GET', 'POST'))
def login(auth: AuthManager):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            auth.login(form.email.data, form.password.data)
        except LoginException as e:
            form.email.errors.append(str(e))
            return render_template('auth/login.html', form=form)

        resp = make_response(redirect(url_for('main.index')))
        resp.set_cookie('auth_token', jwt.create_token(current_user.profile), max_age=60*60*24*360)

        return resp

    return render_template('auth/login.html', form=form)


@bp.route('logout')
def logout(auth_service: AuthManager):
    auth_service.logout()
    return redirect(url_for('auth.login'))


@bp.route('register', methods=('GET', 'POST'))
def register(city_repo: CityRepo, user_registration: UserRegistration, auth_manager: AuthManager):
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
        auth_manager.login_user(user)
        resp = make_response(redirect(url_for('main.profile', profile_id=user.profile.id)))
        resp.set_cookie('auth_token', jwt.create_token(current_user.profile), max_age=60*60*24*360)

        return resp

    return render_template('auth/register.html', form=form)
