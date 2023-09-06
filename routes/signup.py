from flask import (
    Blueprint, render_template, 
    redirect, url_for, request, flash
)
from ..models import User, Role
from ..helpers import generate_hash
from .. import db
from ..forms import SignUpForm



signup_blueprint = Blueprint('signup', __name__)


@signup_blueprint.route('/signup')
def index():
    form = SignUpForm()
    return render_template('signup.html', form=form)


@signup_blueprint.route('/signup')
def signup():
    signup_form = SignUpForm(request.form)
    return render_template('signup.html', form=signup_form)


@signup_blueprint.route('/signup', methods=['POST'])
def signup_post():
    signup_form = SignUpForm(request.form)
    if not signup_form.validate():
        return render_template('signup.html', form=signup_form, errors=signup_form.errors)

    user = User.query.filter_by(email=signup_form.email.data).first()
    if user:
        flash('Email address already exist.', 'error')
        return render_template('signup.html', form=signup_form)
    
    # create a new user with the form data. 
    # Hash the password so the plaintext version isn't saved.
    new_user = User(
        email=signup_form.email.data, 
        name=signup_form.name.data, 
        password=generate_hash(signup_form.password.data.encode('utf-8'), method='sha256')
    )
    resp = ('Successfully created the account.', 'message')
    try:
        # add default role (Analyst)
        r = Role.query.filter_by(name='Analyst').first()
        # add the new user to the database
        new_user.roles.append(r)
        db.session.add(new_user)
        db.session.commit()
    except:
        resp = ('Error creating the account.', 'error')    
    
    flash(resp[0], resp[1])
    return redirect(url_for('login.index'))
