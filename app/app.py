import os

from flask import render_template
from werkzeug.exceptions import NotFound

from app import create_app
from app.database.repositories import ProfileRepo

app = create_app(env=os.environ.get('ENV'))


@app.route('/')
def index():
    return 'hello world'


@app.route('/<profile_id>')
def person(profile_id: int):
    profile = ProfileRepo.find_by_id(profile_id)
    if profile is None:
        raise NotFound('Profile not found')
    return render_template('profile.html', profile=profile)


@app.route('/friends')
def friends():
    return 'friends'


@app.route('/friends/add')
def add_friend():
    return 'friends'


@app.route('/friends/delete')
def delete_friend():
    return 'friends'
