from flask import render_template, Blueprint
from flask_login import login_required

from app.jwt import jwt_cookie_required
from app.service_discovery import ServiceDiscovery

bp = Blueprint('dialogs', __name__, url_prefix='/dialogs')


@bp.route('/')
@login_required
@jwt_cookie_required
def index(sd: ServiceDiscovery):
    return render_template(
        'dialogs/index.html',
        chat_url=sd.service('dialogs-app').address,
    )

