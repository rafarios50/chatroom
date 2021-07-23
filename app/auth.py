import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.dbschema import User

#Blueprint that manages the registration, login and logout of users to the app
bp = Blueprint('auth', __name__, url_prefix='/auth')

#View for register new users
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif User.find_user(username) is not None:      
            error = f"User {username} is already registered."
        if error is None:
            #Register the user into the db and returns to the login page
            userObj = User(username, generate_password_hash(password))
            userObj.register_user()
            return redirect(url_for('auth.login'))
        flash(error)
    return render_template('auth/register.html')

#View to login into the chatroom index
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = User.find_user(username)
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))
        flash(error)
    return render_template('auth/login.html')

#Check if user is logged in before any app request
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.find_user_by_id(user_id)

#View to logout an user, removing it from the session and redirecting to the index page
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#decorator to evaluate if the user is logged in before getting into a chatroom
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view   