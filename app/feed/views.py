from flask import render_template, request, Blueprint, redirect, url_for, jsonify
from flask_login import login_required, current_user

from app.database.models import Post
from app.database.repositories import PostsRepo
from app.feed.forms import PostAddForm

bp = Blueprint('feed', __name__, url_prefix='/feed')


@bp.route('/')
@login_required
def index(posts_repo: PostsRepo):
    page = request.args.get('page', default=1, type=int)
    collection = posts_repo.find_paginate(page, count=10, order='desc')
    return render_template(
        'feed/index.html',
        pagination=collection.pagination,
        posts=collection.items,
        form=PostAddForm()
    )


@bp.route('/', methods=['POST'])
@login_required
def add(posts_repo: PostsRepo):
    form = PostAddForm(request.form)
    if not form.validate():
        return jsonify({
            'success': False,
            'errors': form.errors
        })

    posts_repo.save(Post(author_id=current_user.profile_id, content=form.content.data))
    posts_repo.db.commit()

    return jsonify({
        'success': True,
        'redirect': url_for('feed.index')
    })

