from flask import render_template, request, Blueprint, url_for, jsonify
from flask_login import login_required, current_user
from injector import inject

from app.feed.forms import PostAddForm
from app.feed.services import FeedService, PostService

bp = Blueprint('feed', __name__, url_prefix='/feed')


@bp.route('/')
@login_required
@inject
def index(feed: FeedService):
    page = request.args.get('page', default=1, type=int)
    collection = feed.load(feed_id=current_user.profile_id, page=page, count=10)
    return render_template(
        'feed/index.html',
        pagination=collection.pagination,
        posts=collection.items,
        form=PostAddForm()
    )


@bp.route('/', methods=['POST'])
@login_required
@inject
def add(post_service: PostService):
    form = PostAddForm(request.form)
    if not form.validate():
        return jsonify({
            'success': False,
            'errors': form.errors
        })

    post_service.create(current_user.profile, form.content.data)

    return jsonify({
        'success': True,
        'redirect': url_for('feed.index')
    })

