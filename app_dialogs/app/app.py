import os

from app import create_app

app = create_app(env=os.environ.get('ENV'))


@app.route('/')
def index():
    return 'Dialogs app'
