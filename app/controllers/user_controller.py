from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, logout_user, login_required
from app.models import User
from app import db, bcrypt

user_bp = Blueprint('user', __name__)

@user_bp.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        hashed_password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        user = User(username=request.form['username'], password=hashed_password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('sign-up-form.html', title='Sign Up')

@user_bp.route('/log-in', methods=['GET', 'POST'])
def log_in():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('recipes.recipes_list'))
    return render_template('log-in.html', title='Log In')

@user_bp.route('/log-out')
@login_required
def log_out():
    logout_user()
    return redirect(url_for('main.index'))