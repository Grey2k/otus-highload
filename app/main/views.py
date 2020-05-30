from flask import render_template, request, Blueprint
from flask_login import login_required, current_user
from werkzeug.exceptions import NotFound

from app.database.repositories import ProfileRepo, CityRepo, FriendRepo

bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/')
@login_required
def index(city_repo: CityRepo, profile_repo: ProfileRepo):
    page = request.args.get('page', default=1, type=int)
    collection = profile_repo.find_paginate(page)
    cities = city_repo.find_by_ids({p.city_id for p in collection.items})
    return render_template(
        'index.html',
        profiles=collection.items,
        pagination=collection.pagination,
        cities=cities
    )


@bp.route('/<profile_id>')
@login_required
def profile(profile_id: int, city_repo: CityRepo, profile_repo: ProfileRepo, friend_repo: FriendRepo):
    p = profile_repo.find_by_id(profile_id)
    if p is None:
        raise NotFound('Profile not found')
    return render_template(
        'profile.html',
        profile=p,
        city=city_repo.find_by_id(p.city_id),
        friendship=friend_repo.find_friendship(p.id, current_user.profile_id) if p.id != current_user.profile_id else None
    )
