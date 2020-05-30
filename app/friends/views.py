from flask import render_template, request, jsonify, Blueprint
from flask_login import login_required, current_user

from app.database.models import User
from app.database.repositories import FriendRepo
from app.friends.services import FriendshipManager

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
def add_friend(friendship_manager: FriendshipManager):
    friendship_manager.start_friendship(current_user.profile_id, request.form.get('friend_id', type=int))
    return jsonify({
        'success': True,
    })


@bp.route('delete', methods=['POST'])
@login_required
def delete_friend(friendship_manager: FriendshipManager):
    friendship_manager.stop_friendship(current_user.profile_id, request.form.get('friend_id', type=int))
    return jsonify({
        'success': True
    })
