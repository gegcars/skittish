from flask import (
    Blueprint, render_template, 
    flash, url_for, redirect, request, session
)
from flask_login import login_required, current_user
from .search import search
from ..models import User, Role
from ..forms import RoleForm, SearchForm
from .. import db, role_required, AVAILABLE_ROLES


role_blueprint = Blueprint('role', __name__)


def create(role_form):
    resp = ('{0} role successfully created.'.format(role_form.name.data), 'message')
    role_id = None
    try:
        # protection for Admin role
        if role_form.name.data.upper() == 'ADMIN':
            resp = ('{0} is a reserved role name.'.format(role_form.name.data), 'error')
            return resp
        
        role = Role.query.filter_by(name=role_form.name.data).first()
        if role:
            resp = ('Role {0} already exist.'.format(role_form.name.data), 'error')
            return resp
        
        # create Role
        role = Role(
            name=role_form.name.data,
            display_name=role_form.display_name.data,
            description=role_form.description.data
        )
        db.session.add(role)
        db.session.commit()
        role_id = role.id

    except Exception as e:
        resp = (e, 'error')
    
    return resp, role_id


def edit(id, role_form):
    resp = ('Edit success for RoleID: {0}'.format(id), 'message')
    try:
        # fetch role by id
        role = Role.query.filter_by(id=id).first()
        if not role:
            resp = ('Role {0} does not exist.'.format(role_form.name.data), 'error')
            return resp
        
        # protection for Admin role (this means that description can be updated)
        if role.name.upper() == 'ADMIN' and role.name != role_form.name.data:
            resp = ('Changing the name of Admin role is not allowed.', 'error')
            return resp

        # update role from POST data
        role.name = role_form.name.data
        role.description = role_form.description.data
        db.session.add(role)
        db.session.commit()

    except Exception as e:
        resp = (e, 'error')

    return resp


def delete(id):
    resp = ('Delete success for RoleID: {0}'.format(id), 'message')
    try:
        # fetch role by id
        role = Role.query.filter_by(id=id).first()
        if not role:
            resp = ('RoleID: {0} does not exist.'.format(id), 'error')
            return resp
        # protection for Admin role
        if role.name.upper() == 'ADMIN':
            resp = ('Admin role cannot be deleted.', 'error')
            return resp

        # delete role from POST data
        db.session.delete(role)
        db.session.commit()

    except Exception as e:
        resp = (e, 'error')

    return resp


@role_blueprint.route('/role')
@login_required
@role_required(role=['admin'])
def index():
    # set message format as tuple
    # ('<MESSAGE>', '<message|success|info|>')
    message = None,
    # set error format as following
    # {'<key>': ['<message1>', '<message2>']}
    errors = None
    is_table = True
    table = []
    role_form = RoleForm()
    search_form = SearchForm()
    # make sure file_search is empty when 
    # showall clicked or /role URL 
    if 'role_search' in session:
        session['role_search'] = ''
    # set item_per_page to 5
    search_form.item_per_page.data = 5
    table = search('roles', search_form, 1)
    session['role_item_per_page'] = int(search_form.item_per_page.data)
    search_form.item_per_page.data = session['role_item_per_page']
        
    return render_template('role.html', 
                           form=search_form if is_table else role_form,
                           table=table, 
                           is_table=is_table,
                           action='show',
                           message=message,
                           errors=errors)


@role_blueprint.route('/role/<regex("view|create|edit|save|delete|search"):action>', methods=['GET'])
@role_blueprint.route('/role/<regex("view|create|edit|save|delete|search"):action>/<int:id>', methods=['GET'])
@role_blueprint.route('/role/<regex("view|create|edit|save|delete|search"):action>/<int:id>/<int:per_page>', methods=['GET'])
@login_required
@role_required(role=['admin'])
def role(action, id=None, per_page=0):
    # # set message format as tuple
    # # ('<MESSAGE>', '<message|success|info>')
    # message = None,
    # # set error format as following
    # # {'<key>': ['<message1>', '<message2>']}
    # errors = None
    is_table = False
    table = []
    role_form = RoleForm()
    search_form = SearchForm()
    # in cases of action == search
    if id == None:
        page = 1
    else:
        page = id
    
    if per_page == 0:
        if 'role_item_per_page' in session:
            search_form.item_per_page.data = session['role_item_per_page']
        else:
            search_form.item_per_page.data = 5
            session['role_item_per_page'] = 5
    else:
        search_form.item_per_page.data = per_page
        session['role_item_per_page'] = per_page

    if action not in ['view', 'create', 'edit', 'save', 'delete', 'search']:
        flash('Not a valid action.', 'error')
        # return to current user profile
        if request.referrer:
            return redirect(request.referrer)
        else:
            return redirect(url_for('user.index'))
        
    try:
        match action:
            case 'create':
                role_form.id.data = ''
                role_form.name.data = ''
                role_form.display_name.data = ''
                role_form.description.data = ''

            case 'search':
                if 'role_search' in session:
                    search_form.search.data = session['role_search']
                table = search('roles', search_form, page)
                is_table = True
                
            case _:
                # get role object by id
                role_obj = Role.query.filter_by(id=id).first()
                # fill RoleForm fields with role object data
                role_form.id.data = role_obj.id
                role_form.name.data = role_obj.name
                role_form.display_name.data = role_obj.display_name
                role_form.description.data = role_obj.description

    except Exception as e:
        flash(e, 'error')
        print(e)
    
    return render_template('role.html', 
                           form=search_form if is_table else role_form,
                           table=table, 
                           is_table=is_table,
                           action=action)


@role_blueprint.route('/role/<regex("view|create|edit|save|delete|search"):action>', methods=['POST'])
@role_blueprint.route('/role/<regex("view|create|edit|save|delete|search"):action>/<int:id>', methods=['POST'])
@role_blueprint.route('/role/<regex("view|create|edit|save|delete|search"):action>/<int:id>/<int:per_page>', methods=['POST'])
@login_required
@role_required(role=['admin'])
def role_post(action, id=None, per_page=0):
    # # set message format as tuple
    # # ('<MESSAGE>', '<message|success|info>')
    # message = None,
    # # set error format as following
    # # {'<key>': ['<message1>', '<message2>']}
    # errors = None
    is_table = False
    table = []
    role_form = RoleForm()
    search_form = SearchForm()
    # set id to page for cases of action == search
    if id == None:
        page = 1
    else:
        page = id
    if per_page == 0:
        if 'role_item_per_page' in session:
            search_form.item_per_page.data = session['role_item_per_page']
        else:
            search_form.item_per_page.data = 5
            session['role_item_per_page'] = 5
    else:
        search_form.item_per_page.data = per_page
        session['role_item_per_page'] = per_page

    if action not in ['view', 'create', 'edit', 'save', 'delete', 'search']:
        flash('Not a valid action.', 'error')
        # return to current user profile
        if request.referrer:
            return redirect(request.referrer)
        else:
            return redirect(url_for('user.index'))
        
    try:
        # validate POST data
        if action != 'search':
            role_form = RoleForm(request.form)
            if not role_form.validate():
                return render_template('role.html', 
                                    form=role_form, 
                                    action=action, 
                                    errors=role_form.errors)        
        else:
            search_form = SearchForm(request.form)
            is_table = True
            if not search_form.validate():
                return render_template('role.html', 
                                    form=search_form, 
                                    action=action, 
                                    errors=search_form.errors)
            session['role_item_per_page'] = int(search_form.item_per_page.data)
            search_form.item_per_page.data = session['role_item_per_page']
            session['role_search'] = search_form.search.data
        
        # process POST data
        match action:
            case 'create':
                message, role_id = create(role_form)
                flash(*message)
                if role_id:
                    return redirect(url_for('role.role', action='view', id=role_id))
                
            case action if action in ['edit', 'save']:
                message = edit(id, role_form)
                flash(*message)

            case 'delete':
                message = delete(id)
                flash(*message)
                return redirect(url_for('role.index'))

            case 'search':
                table = search('roles', search_form, page)

    except Exception as e:
        flash(e, 'error')
        print(e)

    return render_template('role.html', 
                           form=search_form if is_table else role_form, 
                           is_table=is_table,
                           table=table,
                           action=action)
    
    