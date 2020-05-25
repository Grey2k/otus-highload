from flask import render_template, request, g, jsonify, Blueprint

from app.auth import login_required
from app.database.models import Friendship
from app.database.repositories import FriendRepo

bp = Blueprint('friends', __name__, url_prefix='/friends')


@bp.route('/')
@login_required
def friends(friend_repo: FriendRepo):
    return render_template(
        'friends.html',
        friends=friend_repo.find_friends(g.profile.id),
        incoming_requests=friend_repo.find_incoming_requests(g.profile.id),
        outgoing_requests=friend_repo.find_outgoing_requests(g.profile.id),
    )


@bp.route('add', methods=['POST'])
@login_required
def add_friend(friend_repo: FriendRepo):
    me = g.profile.id
    friend_id = request.form.get('friend_id', type=int)
    friendship = friend_repo.find_friendship(me, friend_id)
    if friendship:
        friendship.status = 1
        friend_repo.update(friendship)
    else:
        friendship = Friendship(source_id=me, destination_id=friend_id, status=0)
        friend_repo.create(friendship)

    return jsonify({
        'success': True,
    })


@bp.route('delete', methods=['POST'])
def delete_friend(friend_repo: FriendRepo):
    me = g.profile.id
    friend_id = request.form.get('friend_id', type=int)
    friendship = friend_repo.find_friendship(me, friend_id)
    if friendship:
        friend_repo.remove(friendship)
    return jsonify({
        'success': True
    })
