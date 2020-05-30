from wtforms import Form, StringField, validators, PasswordField, TextAreaField, DateField, SelectField, ValidationError

from app import di
from app.database.repositories import UserRepo


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
