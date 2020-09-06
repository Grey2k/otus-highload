from flask import render_template, request, Blueprint, current_app
from flask_login import login_required, current_user
from werkzeug.exceptions import NotFound

from app.database.repositories import ProfileRepo, CityRepo, FriendRepo, Spec
from app.tarantool.repositories import TarantoolProfilesRepo

bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/')
@login_required
def index(city_repo: CityRepo, profile_repo: TarantoolProfilesRepo):
    page = request.args.get('page', default=1, type=int)
    collection = profile_repo.find_paginate(page, count=30)
    cities = city_repo.use_slave().find_by_ids({p.city_id for p in collection.items})
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
        chat_url=current_app.config.get('CHAT_SERVICE_URL'),
        profile=p,
        city=city_repo.find_by_id(p.city_id),
        friendship=friend_repo.find_friendship(
            p.id, current_user.profile_id) if p.id != current_user.profile_id else None
    )


@bp.route('/search')
@login_required
def search(city_repo: CityRepo, profile_repo: ProfileRepo):
    page = request.args.get('page', default=1, type=int)
    first_name = request.args.get('first_name', type=str, default='')
    last_name = request.args.get('last_name', type=str, default='')
    spec = Spec()
    if first_name:
        spec.where('first_name like %(first_name)s', {'first_name': first_name + '%'})
    if last_name:
        spec.where('last_name like %(last_name)s', {'last_name': last_name + '%'})
    collection = profile_repo.use_slave().find_by_spec(spec, page, count=30)
    cities = city_repo.use_slave().find_by_ids({p.city_id for p in collection.items}) if collection.items else []
    return render_template(
        'search.html',
        profiles=collection.items,
        pagination=collection.pagination,
        cities=cities,
    )
