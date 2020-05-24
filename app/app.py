import os

from flask import render_template, request, g, jsonify
from werkzeug.exceptions import NotFound

from app import create_app
from app.auth import login_required
from app.database.models import Friendship
from app.database.repositories import ProfileRepo, CityRepo, FriendRepo

app = create_app(env=os.environ.get('ENV'))


@app.route('/')
@login_required
def index():
    page = request.args.get('page', default=1, type=int)
    collection = ProfileRepo.find_paginate(page)
    cities_ids = {p.city_id for p in collection.items}
    cities = CityRepo.find_by_ids(cities_ids)
    return render_template(
        'index.html',
        profiles=collection.items,
        pagination=collection.pagination,
        cities=cities
    )


@app.route('/<profile_id>')
@login_required
def profile(profile_id: int):
    p = ProfileRepo.find_by_id(profile_id)
    if p is None:
        raise NotFound('Profile not found')
    return render_template(
        'profile.html',
        profile=p,
        city=CityRepo.find_by_id(p.city_id),
        friendship=FriendRepo.find_friendship(p.id, g.profile.id) if p.id != g.profile.id else None
    )


@app.route('/friends')
@login_required
def friends():
    return render_template(
        'friends.html',
        friends=FriendRepo.find_all(g.profile.id),
        incoming_requests=FriendRepo.find_incoming_requests(g.profile.id),
        outgoing_requests=FriendRepo.find_outgoing_requests(g.profile.id),
    )


@app.route('/friends/add', methods=['POST'])
@login_required
def add_friend():
    me = g.profile.id
    friend_id = request.form.get('friend_id', type=int)
    friendship = FriendRepo.find_friendship(me, friend_id)
    if friendship:
        friendship.status = 1
        FriendRepo.update(friendship)
    else:
        friendship = Friendship(source_id=me, destination_id=friend_id, status=0)
        FriendRepo.create(friendship)

    return jsonify({
        'success': True,
    })


@app.route('/friends/delete', methods=['POST'])
def delete_friend():
    me = g.profile.id
    friend_id = request.form.get('friend_id', type=int)
    friendship = FriendRepo.find_friendship(me, friend_id)
    if friendship:
        FriendRepo.remove(friendship)
    return jsonify({
        'success': True
    })
