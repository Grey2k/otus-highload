import os

from app import create_app
from app.database.db import db

app = create_app(env=os.environ.get('ENV'))


@app.route('/health')
def health():
    try:
        db.master.query('SELECT 1')
    except:
        return '', 500
    return 'ok'
