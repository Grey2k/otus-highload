from flask import Blueprint, request, render_template, redirect, url_for

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('login', methods=('GET', 'POST'))
def login():
    return 'login'


@bp.route('logout')
def logout():
    return 'logout'


@bp.route('register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('auth/register.html')
