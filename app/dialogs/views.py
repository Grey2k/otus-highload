from flask import render_template, Blueprint, current_app
from flask_login import login_required

bp = Blueprint('dialogs', __name__, url_prefix='/dialogs')


@bp.route('/')
@login_required
def index():
    return render_template(
        'dialogs/index.html',
        chat_url=current_app.config.get('CHAT_SERVICE_URL'),
    )

