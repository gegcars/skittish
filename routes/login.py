from flask import (
    Blueprint, render_template, redirect, 
    request, url_for, flash, session
)
from flask_login import login_user, confirm_login, current_user
from ..helpers import check_password_hash
from ..models import User, Role, Report, File
from ..forms import LoginForm



tables = [
    User.__tablename__,
    Role.__tablename__,
    File.__tablename__,
    Report.__tablename__
]
login_blueprint = Blueprint('login', __name__)


@login_blueprint.route('/login')
def index():
    session['tables'] = sorted(tables)
    login_form = LoginForm(request.form)
    # Already logged-in
    if current_user.is_authenticated:
        flash('You are already logged-in.', 'message')
        return redirect(url_for('user.index'))
    
    return render_template('login.html', form=login_form)


@login_blueprint.route('/login', methods=['GET'])
def login():
    session['tables'] = tables
    login_form = LoginForm(request.form)
    # Already logged-in
    if current_user.is_authenticated:
        flash('You are already logged-in.', 'message')
        return redirect(url_for('user.index'))
    
    return render_template('login.html', form=login_form, error=login_form.errors)


@login_blueprint.route('/login', methods=['POST'])
def login_post():
    login_form = LoginForm(request.form)
    if not login_form.validate():
        return render_template('login.html', form=login_form, errors=login_form.errors)
    
    if not login_form.email.data or login_form.email.data == '':
        flash('Please enter email address.', 'error')
        return render_template('login.html', form=login_form)
    
    if not login_form.password.data or login_form.password.data == '':
        flash('Please enter password.', 'error')
        return render_template('login.html', form=login_form)
    
    user = User.query.filter_by(email=login_form.email.data).first()

    if not user.is_active:
        flash('Login failed. This account is not active.', 'error')
        return render_template('login.html', form=login_form)
        
    if not user:
        flash('Login failed. Please check your email address.', 'error')
        return render_template('login.html', form=login_form)
    
    if not check_password_hash(user.password, login_form.password.data.encode('utf-8')):
        flash('Login failed. Email address does not match with password.', 'error')
        return render_template('login.html', form=login_form)
    
    login_user(user, remember=login_form.remember_me)
    
    if 'admin' in [n.name for n in user.roles]:
        setattr(current_user, 'is_admin', True)
        session['is_admin'] = True
    else:
        setattr(current_user, 'is_admin', False)
        session['is_admin'] = False
    
    
    return redirect(url_for('user.index'))