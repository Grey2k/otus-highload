import os

from app import create_app

app = create_app(env=os.environ.get('ENV'))


@app.route('/')
def index():
    return 'hello world'


@app.route('/<int:uid>')
def person(uid: int):
    return 'hello world'


@app.route('/friends')
def friends():
    return 'friends'


@app.route('/friends/add')
def add_friend():
    return 'friends'


@app.route('/friends/delete')
def delete_friend():
    return 'friends'
