from flask import (
    Blueprint, render_template, session, flash, request
)
from flask_login import login_required
from ..models import User, Role, Report
from ..forms import SearchForm
from .. import role_required


admin_blueprint = Blueprint('admin', __name__)



def search_users(search_form, page):
    # search users table using email or name
    results = []
    search_data = search_form.search.data
    if not search_data:
        search_data = 'all'
    if search_data.upper() in ['ALL', '*']:
        results = User.query.paginate(page=page, 
                                      per_page=search_form.item_per_page.data, 
                                      error_out=True, 
                                      max_per_page=5)
        return results
    # else search using the search criteria
    results = User.query.filter(
    (User.name.ilike("%"+search_data+"%")) | (User.email.ilike("%"+search_data+"%"))
                                ).paginate(page=page,
                                           per_page=search_form.item_per_page.data, 
                                           error_out=True, 
                                           max_per_page=5)
    return results


def search_roles(search_form, page):
    # search users table using email or name
    results = []
    search_data = search_form.search.data
    if not search_data:
        search_data = 'all'
    if search_data.upper() in ['ALL', '*']:
        results = Role.query.paginate(page=page, 
                                      per_page=search_form.item_per_page.data, 
                                      error_out=True, 
                                      max_per_page=5)
        return results
    # else search using the search criteria
    results = Role.query.filter(
    (Role.name.ilike("%"+search_data+"%")) | (Role.description.ilike("%"+search_data+"%"))
                                ).paginate(page=page,
                                           per_page=search_form.item_per_page.data, 
                                           error_out=True, 
                                           max_per_page=5)
    return results


def search_reports(search_form, page):
    # search reports table using hash or email address
    results = []
    search_data = search_form.search.data
    if not search_data:
        search_data = '*'
    if search_data.upper() in ['ALL', '*']:
        results = Report.query.paginate(page=page, 
                                      per_page=search_form.item_per_page.data, 
                                      error_out=True, 
                                      max_per_page=5)
    else:
        # check for email or name from users table
        users = User.query.filter(
    (User.name.ilike("%"+search_data+"%")) | (User.email.ilike("%"+search_data+"%"))
                                ).all()
        # check for Hash
        results = Report.query.filter(
                (Report.hash.ilike("%"+search_data+"%")) | (Report.user_id.in_([user.id for user in users]))
                                      ).paginate(page=page, 
                                                 per_page=search_form.item_per_page.data, 
                                                 error_out=True, 
                                                 max_per_page=5)

    if results:
        # change report.user_id with user.email for visual
        for report in results:
            setattr(report, 'user_id', User.query.filter_by(id=report.user_id).first().email)

    return results


@admin_blueprint.route('/admin', methods=['GET'])
@login_required
@role_required(role=['admin'])
def index():
    # Default view is Users Table
    session['table_name']  = User.__tablename__
    session['user_item_per_page'] = 5
    session['previous_table'] = 'users'
    users = User.query.paginate(page=1, 
                                per_page=session['user_item_per_page'], 
                                error_out=True, 
                                max_per_page=5)
    
    return render_template('admin.html', table=users, item_per_page=session['user_item_per_page'])


@admin_blueprint.route('/admin/<table_name>', methods=['GET'])
@admin_blueprint.route('/admin/<table_name>/<page>', methods=['GET'])
@admin_blueprint.route('/admin/<table_name>/<page>/<item_per_page>', methods=['GET'])
@login_required
@role_required(role=['admin'])
def admin(table_name, page=1, item_per_page=None):
    table_data = []
    session['table_name'] = table_name
    if 'previous_table' not in session:
        session['previous_table'] = table_name
    # make sure item_per_page and page are int
    if type(item_per_page) == str:
        item_per_page = int(item_per_page)
    if type(page) == str:
        page = int(page)

    search_form = SearchForm()
    # Proceed on querying
    if table_name == 'users':
        # remove previous searches from other tables
        if 'role_search' in session:
            session.pop('role_search')
        if 'role_item_per_page' in session:
            session.pop('role_item_per_page')
        if 'report_search' in session:
            session.pop('report_search')
        if 'report_iter_item_page' in session:
            session.pop('report_iter_item_page')
        # save item_per_page, page in session
        if 'user_item_per_page' not in session:
            session['user_item_per_page'] = 5    
        if item_per_page != None:
            session['user_item_per_page'] = item_per_page
            # search_form.item_per_page.data = item_per_page
        # else:
        search_form.item_per_page.data = session['user_item_per_page']
        if session['previous_table'] != 'users':
            search_form.item_per_page.data = 5 
            session['user_item_per_page'] = 5
        if page <= 0 or session['user_item_per_page'] <= 0:
            flash('The request is not allowed.', 'error')
            return render_template('admin.html', form=search_form, 
                                table=table_data)#, item_per_page=item_per_page)
        if 'user_search' in session:
            search_form.search.data = session['user_search']
        table_data = search_users(search_form, page)        

    elif table_name == 'roles':
        # remove previous searches from other tables
        if 'user_search' in session:
            session.pop('user_search')
        if 'user_item_per_page' in session:
            session.pop('user_item_per_page')
        if 'report_search' in session:
            session.pop('report_search')
        if 'report_iter_item_page' in session:
            session.pop('report_iter_item_page')
        # save item_per_page, page in session
        if 'role_item_per_page' not in session:
            session['role_item_per_page'] = 5    
        if item_per_page != None:
            session['role_item_per_page'] = item_per_page
            # search_form.item_per_page.data = item_per_page
        # else:
        search_form.item_per_page.data = session['role_item_per_page']
        if session['previous_table'] != 'roles':
            search_form.item_per_page.data = 5 
            session['role_item_per_page'] = 5
        if page <= 0 or session['role_item_per_page'] <= 0:
            flash('The request is not allowed.', 'error')
            return render_template('admin.html', form=search_form, 
                                table=table_data)#, item_per_page=item_per_page)
        if 'role_search' in session:
            search_form.search.data = session['role_search']
        table_data = search_roles(search_form, page)

    elif table_name == 'reports':
        # remove previous searches from other tables
        if 'role_search' in session:
            session.pop('role_search')
        if 'role_item_per_page' in session:
            session.pop('role_item_per_page')
        if 'user_search' in session:
            session.pop('user_search')
        if 'user_iter_item_page' in session:
            session.pop('user_iter_item_page')
        # save item_per_page, page in session
        if 'report_item_per_page' not in session:
            session['report_item_per_page'] = 5  
        if item_per_page != None:
            session['report_item_per_page'] = item_per_page
            # search_form.item_per_page.data = item_per_page
        # else:
        search_form.item_per_page.data = session['report_item_per_page']
        if session['previous_table'] != 'reports':
            search_form.item_per_page.data = 5 
            session['report_item_per_page'] = 5
        if page <= 0 or session['report_item_per_page'] <= 0:
            flash('The request is not allowed.', 'error')
            return render_template('admin.html', form=search_form, 
                                table=table_data)#, item_per_page=item_per_page)
        if 'report_search' in session:
            search_form.search.data = session['report_search']
        table_data = search_reports(search_form, page)
    else:
        flash('{0} is unknown table.'.format(table_name), 'error')

    session['previous_table'] = table_name

    return render_template('admin.html', form=search_form,
                           table=table_data) #, item_per_page=session['item_per_page'])


@admin_blueprint.route('/admin/<table_name>', methods=['POST'])
@login_required
@role_required(role=['admin'])
def admin_post(table_name):
    table_data = []
    # validate POST data
    search_form = SearchForm(request.form)
    if not search_form.validate():
        return render_template('admin.html', form=search_form, 
                               table=table_data, #item_per_page=session['item_per_page'],
                               errors=search_form.errors)
    # make sure item_per_page is int
    search_form.item_per_page.data = int(search_form.item_per_page.data)
    
    if table_name == 'users':
        session['user_search'] = request.form.get('search')
        session['user_item_per_page'] = search_form.item_per_page.data
        table_data = search_users(search_form, 1)
    
    elif table_name == 'roles':
        session['role_search'] = request.form.get('search')
        session['role_item_per_page'] = search_form.item_per_page.data
        table_data = search_roles(search_form, 1)
    elif table_name == 'reports':
        session['report_search'] = request.form.get('search')
        session['report_item_per_page'] = search_form.item_per_page.data
        table_data = search_reports(search_form, 1)

    return render_template('admin.html', form=search_form, table=table_data)
