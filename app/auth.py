from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import logout_user, current_user, login_user
from injector import inject
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, StringField, validators, PasswordField, TextAreaField, DateField, SelectField, ValidationError

from app import di
from app.database.db import db
from app.database.models import User, Profile
from app.database.repositories import CityRepo, UserRepo, ProfileRepo


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


class RegistrationForm(Form):
    email = StringField('E-mail', [validators.Email()])
    first_name = StringField('First name', [validators.DataRequired()])
    last_name = StringField('Last name', [validators.DataRequired()])
    interests = TextAreaField('Interests', [validators.DataRequired()])
    birth_date = DateField('Birth date')
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female')])
    city = SelectField('City', coerce=int)
    password = PasswordField('Password', [
        validators.Length(min=6),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')

    def validate_email(form, field):
        # todo: Исправить
        user_repo: UserRepo = di.get(UserRepo)
        if user_repo.find_by_email(field.data) is not None:
            raise ValidationError('E-mail already registered')


class LoginForm(Form):
    email = StringField('E-mail')
    password = PasswordField('Password')

    def validate_email(form, field):
        # todo: Исправить
        user_repo: UserRepo = di.get(UserRepo)
        user = user_repo.find_by_email(field.data)
        if user is None:
            raise ValidationError('E-mail or password incorrect')
        if not check_password_hash(user.password, form.password.data):
            raise ValidationError('E-mail or password incorrect')
