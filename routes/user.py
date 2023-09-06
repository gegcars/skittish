from flask import (
    Blueprint, render_template, 
    flash, url_for, redirect, 
    request, session
)
from flask_login import login_required, current_user
from .search import search
from ..helpers import generate_hash
from ..models import User, Role, UserRole
from ..forms import UserForm, SearchForm
from .. import db, AVAILABLE_ROLES


user_blueprint = Blueprint('user', __name__)


# create user account
def create(user_form):
    resp = ('Account {0} has been created.'.format(user_form.email.data), 'message')
    id = None
    try:
        user_obj = User.query.filter_by(email=user_form.email.data).first()
        if user_obj:
            resp = ('This email address {0} already exists.'.format(user_form.email.data), 'error')
            return resp
        # create the account
        user_obj = User(
            email=user_form.email.data.lower(),
            name=user_form.name.data,
            password=generate_hash(user_form.password.data.encode('utf-8'))
        )
        roles = user_form.role.data
        for role in roles:
            r = Role.query.filter_by(name=role).first()
            user_obj.roles.append(r)
        # add user account to database
        db.session.add(user_obj)
        db.session.commit()
        id = user_obj.id

    except Exception as e:
        resp = (e, 'error')

    return resp, id

# User update by id
def edit(id, user_form):
    resp = ('UserID: {0} has been updated.'.format(id), 'message')
    try:
        # check at least 1 role
        roles = user_form.role.data
        if len(roles) == 0:
            resp = ('At least 1 role must be added.', 'error')
            return resp
        
        # fetch user by id
        user = User.query.filter_by(id=id).first()
        if not user:
            resp = ('UserID: {0} does not exist.'.format(id), 'error')
            return resp
        
        # protection for user admin@skittish.flask
        if user.email.upper() == 'admin@skittish.flask'.upper() and current_user.id != user.id:
            resp = ('This account is protected.', 'error')
            return resp
        
        # update user with the POST data
        user.email = user_form.email.data.lower()
        user.name = user_form.name.data        

        # Remove existing roles
        user.roles = []
        # Add new roles
        for n in roles:
            r = Role.query.filter_by(name=n).first()
            if not r:
                continue
            user.roles.append(r)
        
        db.session.add(user)
        db.session.commit()
    
    except Exception as e:
        resp = (e, 'error')
    
    return resp


def delete(id):
    resp = ('UserID: {0} has been deleted.'.format(id), 'message')
    try:
        # fetch user by id
        user = User.query.filter_by(id=id).first()
        if not user:
            resp = ('UserID: {0} does not exist.'.format(id), 'error')
            return resp
        
        # protection for user admin@skittish.flask
        if user.email.upper() == 'admin@skittish.flask'.upper() and current_user.id != user.id:
            resp = ('This account is protected.', 'error')
            return resp

        # delete from users table
        db.session.delete(user)

        # delete user from user_roles table
        user_roles = UserRole.query.filter_by(id=id).all()
        for user_role in user_roles:
            db.session.delete(user_role)
        
        # commit changes
        db.session.commit()

    except Exception as e:
        resp = (e, 'error')

    return resp


@user_blueprint.route('/user')
@user_blueprint.route('/user/current')
@login_required
def index():
    # set message format as tuple
    # ('<MESSAGE>', '<message|success|info|>')
    message = None,
    # set error format as following
    # {'<key>': ['<message1>', '<message2>']}
    errors = None
    is_table = False
    table = []
    roles_available = {}
    user_form = UserForm()
    # make sure file_search is empty when 
    # showall clicked or /user or /user/current URL 
    if 'search' in session:
        session['search'] = ''

    user_roles = [r.name for r in current_user.roles]
    if 'admin' in user_roles:
        is_table = True
        search_form = SearchForm()
        # set item_per_page to 5
        search_form.item_per_page.data = 5
        table = search('users', search_form, 1)
        session['item_per_page'] = int(search_form.item_per_page.data)
        search_form.item_per_page.data = session['item_per_page']
        
    else:
        user_form.id.data = current_user.id
        user_form.email.data = current_user.email
        user_form.name.data = current_user.name
        for r in AVAILABLE_ROLES:
            if r in user_roles:
                roles_available[r] = True
            else:
                roles_available[r] = False
        
    return render_template('user.html', 
                           form=search_form if is_table else user_form,
                           table=table, 
                           roles_available=roles_available, 
                           is_table=is_table,
                           action='show',
                           message=message,
                           errors=errors)


@user_blueprint.route('/user/<regex("view|create|edit|save|delete|search"):action>', methods=['GET'])
@user_blueprint.route('/user/<regex("view|create|edit|save|delete|search"):action>/<int:id>', methods=['GET'])
@user_blueprint.route('/user/<regex("view|create|edit|save|delete|search"):action>/<int:id>/<int:per_page>', methods=['GET'])
@login_required
def user(action, id=None, per_page=0):
    # # set message format as tuple
    # # ('<MESSAGE>', '<message|success|info>')
    # message = None,
    # # set error format as following
    # # {'<key>': ['<message1>', '<message2>']}
    # errors = None
    is_table = False
    table = []
    roles_available = {}
    user_form = UserForm()
    search_form = SearchForm()
    if per_page == 0:
        if 'item_per_page' in session:
            search_form.item_per_page.data = session['item_per_page']
        else:
            search_form.item_per_page.data = 5
            session['item_per_page'] = 5
    else:
        search_form.item_per_page.data = per_page
        session['item_per_page'] = per_page

    # set id to page for cases of action == search
    page = id
    # if id is None, current_user.id will be used
    if id == None:
        id = current_user.id
    
    # # get roles of current_user
    # current_user_roles = [r.name for r in current_user.roles]
    # if 'admin' in current_user_roles:
    #     is_admin = True

    # user cannot view other's profile unless they have admin role
    if current_user.id != id and not session['is_admin']:
        flash('The request is not allowed.', 'error')
        return redirect(url_for('user.index'))
    
    # check for valid actions
    if action not in ['view', 'create', 'edit', 'save', 'delete', 'search']:
        flash('Not a valid action.', 'error')
        return redirect(url_for('user.index'))
    
    # search is for admin only
    if action == 'search' and not session['is_admin']:
        flash('The request is not allowed.', 'error')
        return redirect(url_for('user.index'))

    try:
        match action:
            case 'create':
                user_form.id.data = ''
                user_form.name.data = ''
                user_form.email.data = ''
                for r in AVAILABLE_ROLES:
                    roles_available[r] = False # so that it will not have a check mark on HTML
            
            case 'search':
                if 'search' in session:
                    search_form.search.data = session['search']
                table = search('users', search_form, page)
                is_table = True
                    
            case _:
                # User object
                user_obj = User.query.filter_by(id=id).first()
                # fill UserForm field with user objects
                user_form.id.data = user_obj.id
                user_form.email.data = user_obj.email
                user_form.name.data = user_obj.name
                # dictionary of roles of the User
                user_roles = [r.name for r in user_obj.roles]
                user_form.role.data = user_roles
                for r in AVAILABLE_ROLES:
                    if r in user_roles:
                        roles_available[r] = True
                    else:
                        roles_available[r] = False

    except Exception as e:
        flash(e, 'error')
        print(e)

    return render_template('user.html', 
                           form=search_form if is_table else user_form,
                           table=table, 
                           roles_available=roles_available, 
                           is_table=is_table,
                           action=action)


@user_blueprint.route('/user/<regex("view|create|edit|save|delete|search"):action>', methods=['POST'])
@user_blueprint.route('/user/<regex("view|create|edit|save|delete|search"):action>/<int:id>', methods=['POST'])
@login_required
def user_post(action, id=None, per_page=0):
    # set message format as tuple
    # ('<MESSAGE>', '<message|success|info>')
    message = None,
    # set error format as following
    # {'<key>': ['<message1>', '<message2>']}
    errors = None
    is_table = False
    table = []
    roles_available = {}
    user_form = UserForm()
    search_form = SearchForm()
    # set id to page for cases of action == search
    if id == None:
        page = 1
    else:
        page = id
    # # get roles of current_user
    # current_user_roles = [r.name for r in current_user.roles]
    # if 'admin' in current_user_roles:
    #     is_admin = True

    # user cannot view other's profile unless they have admin role
    if current_user.id != id and not session['is_admin']:
        flash('The request is not allowed.', 'error')
        return redirect(url_for('user.index'))
    
    # check for valid actions
    if action not in ['view', 'create', 'edit', 'save', 'delete', 'search']:
        flash('Not a valid action.', 'error')
        return redirect(url_for('user.index'))
    
    # search is for admin only
    if action == 'search' and not session['is_admin']:
        flash('The request is not allowed.', 'error')
        return redirect(url_for('user.index'))
    
    try:
        # roles from Role object (available roles)
        for r in AVAILABLE_ROLES:
            if r in request.form.getlist('role'):
                roles_available[r] = True
            else:
                roles_available[r] = False

        # validate POST data
        if action != 'search':
            user_form = UserForm(request.form)
            if not user_form.validate():
                return render_template('user.html', 
                                form=search_form if is_table else user_form,
                                table=table, 
                                roles_available=roles_available, 
                                is_table=is_table,
                                action=action,
                                message=message,
                                errors=user_form.errors)
        else: # action == search
            search_form = SearchForm(request.form)
            is_table = True
            if not search_form.validate():
                return render_template('user.html', 
                                form=search_form,
                                table=table, 
                                roles_available=roles_available, 
                                is_table=is_table,
                                action=action,
                                message=message,
                                errors=search_form.errors)
            session['item_per_page'] = int(search_form.item_per_page.data)
            search_form.item_per_page.data = session['item_per_page']
            session['search'] = search_form.search.data
        
        # process POST data  
        match action:
            case 'create':
                # extra validation for password and confirm_password
                if not user_form.password.data:
                    flash('password - This field is required.', 'error')
                    return render_template('user.html', 
                                           form=user_form,
                                           roles_available=roles_available, 
                                           action=action)
                
                if len(user_form.password.data) < 8:
                    flash('Password must be between 8-300 characters long. \
                          Use a combination of symbols, numbers, upper and lower case letters.', 'error')
                    return render_template('user.html', 
                                           form=user_form,
                                           roles_available=roles_available, 
                                           action=action)

                if user_form.password.data != user_form.confirm_password.data:
                    flash('Passwords must match.', 'error')
                    return render_template('user.html', 
                                           form=user_form,
                                           roles_available=roles_available, 
                                           action=action)
                # create account
                message, user_id = create(user_form)
                flash(*message)
                if user_id:
                    return redirect(url_for('user.user', action='view', id=user_id))

            case action if action in ['edit', 'save']:
                # user without admin cannot add admin role to itself
                if current_user.id == id and not session['is_admin']:
                    not_allowed = False
                    for k in roles_available:
                        if k == 'admin' and roles_available[k]:
                            not_allowed = True
                            break
                    if not_allowed:
                        flash('The request is not allowed.', 'error')
                        return redirect(url_for('user.index'))
                # save changes to User
                message = edit(id, user_form)
                flash(*message)
                user_form.id.data = id
                return redirect(url_for('user.user', action='view', id=id))

            case 'delete':
                message = delete(id)
                flash(*message)
                return redirect(url_for('user.index'))
            
            case 'search':
                table = search('users', search_form, page)
        
        # make sure id is filled in UserForm
        user_form.id.data = id

    except Exception as e:
        flash(e, 'error')
        print(e)

    return render_template('user.html', 
                           form=search_form if is_table else user_form,
                           table=table, 
                           roles_available=roles_available, 
                           is_table=is_table,
                           action=action,
                           message=message,
                           errors=errors)


