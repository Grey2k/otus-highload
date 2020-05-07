from flask import Blueprint, request, render_template, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, StringField, validators, PasswordField, TextAreaField, DateField, SelectField, ValidationError

from app.database.db import db
from app.database.models import User
from app.database.repositories import CityRepo, UserRepo, ProfileRepo

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('login', methods=('GET', 'POST'))
def login():
    if g.user:
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = UserRepo.find_by_email(form.email.data)
        auth_user(user)
        return redirect(url_for('index'))

    return render_template('auth/login.html', form=form)


@bp.route('logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


@bp.route('register', methods=('GET', 'POST'))
def register():
    if g.user:
        return redirect(url_for('index'))
    form = RegistrationForm(request.form)
    form.city.choices = [(city.id, city.name) for city in CityRepo.find_all()]
    if request.method == 'POST' and form.validate():
        user = UserRepo.create(form.email.data, generate_password_hash(form.password.data))
        profile = ProfileRepo.create(
            first_name=form.first_name.data, last_name=form.last_name.data,
            interests=form.interests.data, birth_date=form.birth_date.data, gender=form.gender.data,
            city_id=form.city.data, user_id=user.id
        )
        db.commit()
        auth_user(user)
        return redirect(url_for('person', profile_id=profile.id))

    return render_template('auth/register.html', form=form)


@bp.before_app_request
def load_logged_in_user():
    uid = session.get('uid')
    g.user = UserRepo.find_by_id(uid) if uid else None


def auth_user(user: User):
    session.clear()
    session['uid'] = user.id


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
        if UserRepo.find_by_email(field.data) is not None:
            raise ValidationError('E-mail already registered')


class LoginForm(Form):
    email = StringField('E-mail')
    password = PasswordField('Password')

    def validate_email(form, field):
        user = UserRepo.find_by_email(field.data)
        if user is None:
            raise ValidationError('E-mail or password incorrect')
        if not check_password_hash(user.password, form.password.data):
            raise ValidationError('E-mail or password incorrect')
