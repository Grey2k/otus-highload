from flask import render_template, request, jsonify, Blueprint
from flask_login import login_required, current_user

from app.database.models import Friendship, User, FriendshipStatus
from app.database.repositories import FriendRepo

bp = Blueprint('friends', __name__, url_prefix='/friends')


@bp.route('/')
@login_required
def friends(friend_repo: FriendRepo):
    user: User = current_user
    return render_template(
        'friends.html',
        friends=friend_repo.find_friends(user.profile_id),
        incoming_requests=friend_repo.find_incoming_requests(user.profile_id),
        outgoing_requests=friend_repo.find_outgoing_requests(user.profile_id),
    )


@bp.route('add', methods=['POST'])
@login_required
def add_friend(friend_repo: FriendRepo):
    me = current_user.profile_id
    friend_id = request.form.get('friend_id', type=int)
    friendship = friend_repo.find_friendship(me, friend_id)
    if friendship:
        friendship.status = FriendshipStatus.CONFIRMED
    else:
        friendship = Friendship(source_id=me, destination_id=friend_id, status=FriendshipStatus.WAITING)
    friend_repo.save(friendship)
    friend_repo.db.commit()

    return jsonify({
        'success': True,
    })


@bp.route('delete', methods=['POST'])
@login_required
def delete_friend(friend_repo: FriendRepo):
    me = current_user.profile_id
    friend_id = request.form.get('friend_id', type=int)
    friendship = friend_repo.find_friendship(me, friend_id)
    if friendship:
        friend_repo.remove(friendship)
    return jsonify({
        'success': True
    })
