from flask import (
    Blueprint, render_template, 
    flash, url_for, redirect, request, 
    session, jsonify
)
from sqlalchemy.orm import load_only
from markupsafe import Markup
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from .search import search
from .save import save_to_pdf
from ..models import User, File, Service, Report
from ..forms import FileForm, SearchForm, ReportForm
from ..helpers import generate_hash
from .. import db, Skittish, role_required, AVAILABLE_SERVICES, UPLOAD_DIR
import os
import base64
import json


file_blueprint = Blueprint('file', __name__)



#########################################
###       FILE action functions       ###
#########################################
def delete(id):
    resp = ('Delete success for FileID: {0}'.format(id), 'message')
    try:
        # fetch file by id
        file = File.query.options(load_only(File.id)).filter_by(id=id).first()
        if not file:
            resp = ('FileID: {0} does not exist.'.format(id), 'error')
            return resp
        
        # delete file from POST data
        db.session.delete(file)
        db.session.commit()

    except Exception as e:
        resp = (e, 'error')

    return resp


#########################################
###           FILE routes             ###
#########################################
@file_blueprint.route('/file')
@login_required
def index():
    # set message format as tuple
    # ('<MESSAGE>', '<message|success|info|>')
    message = None,
    # set error format as following
    # {'<key>': ['<message1>', '<message2>']}
    errors = None
    is_table = True
    table = []
    file_form = FileForm()
    search_form = SearchForm()
    # make sure file_search is empty when 
    # showall clicked or /file URL 
    if 'file_search' in session:
        session['file_search'] = ''
    # set item_per_page to 5
    search_form.item_per_page.data = 5
    table = search('files', search_form, 1)
    session['file_item_per_page'] = int(search_form.item_per_page.data)
    search_form.item_per_page.data = session['file_item_per_page']
        
    return render_template('file.html', 
                           form=search_form if is_table else file_form,
                           table=table, 
                           is_table=is_table,
                           available_services=AVAILABLE_SERVICES,
                           action='show',
                           message=message,
                           errors=errors)


@file_blueprint.route('/file/upload', methods=['POST'])
@login_required
def upload():
    file_upload = request.files['file']
    file = None
    file_form = FileForm()
    data = None
    filename = None
    sha256 = None
    if file_upload.filename == '':
        return jsonify({'file':'empty_file_selection'})
    try:
        data = file_upload.read()
        if len(data) >= 1024*1000*50:
            return jsonify({'file':'file_too_big_50MB_max'})
        
        sha256 = generate_hash(data, 'sha256')
        filename = secure_filename(file_upload.filename)
        if not filename:
            filename = sha256
        # with open(os.path.join(UPLOAD_DIR, filename), 'wb') as ud:
        #     ud.write(data)
        if not data:
            return jsonify({'file':'empty_file'})

        file = File.query.options(
            load_only(File.id, File.filename, File.filesize, File.md5, File.sha1, 
                      File.sha256, File.sha512, File.user_id, File.upload_date)
            ).filter_by(sha256=sha256).first()
        if file:
            flash('already exist - {0}'.format(file.sha256), 'error')
            return jsonify({
                'file': {
                    'filename': file.filename,
                    'filesize': file.filesize,
                    'md5': file.md5,
                    'sha1': file.sha1,
                    'sha256': file.sha256,
                    'sha512': file.sha512
                },
                'message': 'already exist - {0}'.format(file.sha256),
                'error': ''
            })
        else:
            # save it to database
            file = File(
                filename=filename,
                filesize=len(data),
                data=base64.b64encode(data),
                md5=generate_hash(data, 'md5'),
                sha1=generate_hash(data, 'sha1'),
                sha256=sha256,
                sha512=generate_hash(data, 'sha512'),
                user_id=current_user.id
            )
            # the file must be sent for report creation
            service = Service.query.filter_by(name='Report').first()
            file.services.append(service)
            # add it to database
            db.session.add(file)
            db.session.commit() # to get file.id before creating report

            # create the report entry for this file
            report = Report.query.filter_by(file_id=file.id).first()
            report_content = {
                    'title': 'This is a placeholder TITLE for {0}'.format(file.sha256),
                    'content': 'This is a placeholder CONTENT for {0}'.format(file.sha256),
                    'is_published': False
                }
            if not report:
                report = Report(
                    service_id=service.id,
                    file_id=file.id,
                    sha256=file.sha256,
                    content=json.dumps(report_content),
                    requested_by=current_user.id                    
                )
                # add it to database
                db.session.add(report)        
                # commit changes
                db.session.commit()

            print('Success')
        
    except Exception as e:
        flash('Error: {0}'.format(e), 'error')
        print(e)
        return jsonify({
            'file':{},
            'message':'',
            'error': '{0}'.format(e)
        })
    
    # # check if the saved data has still the same hash
    # check_it = File.query.filter_by(sha256=file.sha256).first()
    # if check_it.sha256 == generate_hash(base64.b64decode(check_it.data), 'sha256'):
    #     print('The same SHA256')
    # else:
    #     print('Not the same SHA256')

    return jsonify({
        'file': {
            'filename': file.filename,
            'filesize': file.filesize,
            'md5': file.md5,
            'sha1': file.sha1,
            'sha256': file.sha256,
            'sha512': file.sha512
        },
        'message': 'uploaded - {0}'.format(file_form.filename.data),
        'error': ''
    })


@file_blueprint.route('/file/<regex("view|delete|search"):action>', methods=['GET'])
@file_blueprint.route('/file/<regex("view|delete|search"):action>/<int:id>', methods=['GET'])
@file_blueprint.route('/file/<regex("view|delete|search"):action>/<int:id>/<int:per_page>', methods=['GET'])
@login_required
def file(action, id=None, per_page=0):
    # # set message format as tuple
    # # ('<MESSAGE>', '<message|success|info>')
    # message = None,
    # # set error format as following
    # # {'<key>': ['<message1>', '<message2>']}
    # errors = None
    is_table = False
    table = []
    services_available = {}
    file_form = FileForm()
    search_form = SearchForm()
    # in cases of action == search
    if id == None:
        page = 1
    else:
        page = id
    
    if per_page == 0:
        if 'file_item_per_page' in session:
            search_form.item_per_page.data = session['file_item_per_page']
        else:
            search_form.item_per_page.data = 5
            session['file_item_per_page'] = 5
    else:
        search_form.item_per_page.data = per_page
        session['file_item_per_page'] = per_page

    if action not in ['view', 'upload', 'delete','search']:
        flash('Not a valid action.', 'error')
        # return to current user profile
        if request.referrer:
            return redirect(request.referrer)
        else:
            return redirect(url_for('user.index'))
        
    try:
        match action:
            case 'upload':
                pass #to-do

            case 'search':
                if 'file_search' in session:
                    search_form.search.data = session['file_search']
                table = search('files', search_form, page)
                is_table = True
                
            case _:
                # get file object by id
                file_obj = File.query.options(
                    load_only(File.id, File.filename, File.filesize, File.md5, File.sha1, 
                              File.sha256, File.sha512, File.user_id, File.upload_date)
                              ).filter_by(id=id).first()
                # check the role of current_user
                # the file cannot be viewed if the current_user.id
                # is only submitter
                if 'submitter' in [r.name for r in current_user.roles] and len(current_user.roles) == 1:
                    if file_obj.user_id != current_user.id:
                        flash('You don\'t have the permission to {0} this file.'.format(action), 'error')
                        return render_template('file.html', 
                           form=search_form,
                           table=table, 
                           is_table=True,
                           available_services=AVAILABLE_SERVICES,
                           action=action)

                # transform file object services to {service_name: service_id}
                file_services = {}
                for s in file_obj.services:
                    service = Service.query.filter_by(id=s.id).first()
                    if not service:
                        continue
                    file_services[service.name] = service.id

                # fill FileForm fields with file object data
                file_form.id.data = file_obj.id
                file_form.filename.data = file_obj.filename
                file_form.filesize.data = file_obj.filesize
                file_form.md5.data = file_obj.md5
                file_form.sha1.data = file_obj.sha1
                file_form.sha256.data = file_obj.sha256
                file_form.sha512.data = file_obj.sha512
                file_form.file_services.data = file_services

    except Exception as e:
        flash(e, 'error')
        print(e)
    
    return render_template('file.html', 
                           form=search_form if is_table else file_form,
                           table=table, 
                           is_table=is_table,
                           available_services=AVAILABLE_SERVICES,
                           action=action)


@file_blueprint.route('/file/<regex("view|delete|search"):action>', methods=['POST'])
@file_blueprint.route('/file/<regex("view|delete|search"):action>/<int:id>', methods=['POST'])
@file_blueprint.route('/file/<regex("view|delete|search"):action>/<int:id>/<int:per_page>', methods=['POST'])
@login_required
def file_post(action, id=None, per_page=0):
    # # set message format as tuple
    # # ('<MESSAGE>', '<message|success|info>')
    # message = None,
    # # set error format as following
    # # {'<key>': ['<message1>', '<message2>']}
    # errors = None
    is_table = False
    table = []
    file_form = FileForm()
    search_form = SearchForm()
    # set id to page for cases of action == search
    if id == None:
        page = 1
    else:
        page = id
    if per_page == 0:
        if 'file_item_per_page' in session:
            search_form.item_per_page.data = session['file_item_per_page']
        else:
            search_form.item_per_page.data = 5
            session['file_item_per_page'] = 5
    else:
        search_form.item_per_page.data = per_page
        session['file_item_per_page'] = per_page

    if action not in ['view', 'delete', 'search']:
        flash('Not a valid action.', 'error')
        # return to current user profile
        if request.referrer:
            return redirect(request.referrer)
        else:
            return redirect(url_for('user.index'))
            
    try:
        # validate POST data
        if action != 'search':
            file_form = FileForm(request.form)
            if not file_form.validate():
                return render_template('file.html', 
                                    form=file_form, 
                                    action=action, 
                                    errors=file_form.errors) 
              
        else:
            search_form = SearchForm(request.form)
            is_table = True
            if not search_form.validate():
                return render_template('file.html', 
                                    form=search_form, 
                                    action=action, 
                                    errors=search_form.errors)
            session['file_item_per_page'] = int(search_form.item_per_page.data)
            search_form.item_per_page.data = session['file_item_per_page']
            session['file_search'] = search_form.search.data

        # check the role of current_user
        # the file cannot be viewed if the current_user.id
        # is only submitter
        if 'submitter' in [r.name for r in current_user.roles] and len(current_user.roles) == 1:
            if file_form.user_id != current_user.id:
                flash('You don\'t have the permission to {0} this file.'.format(action), 'error')
                return render_template('file.html', 
                    form=search_form,
                    table=table, 
                    is_table=True,
                    available_services=AVAILABLE_SERVICES,
                    action=action)     
        
        # process POST data
        match action:
            case 'delete':
                message = delete(id)
                flash(*message)
                return redirect(url_for('file.index'))

            case 'search':
                table = search('files', search_form, page)

    except Exception as e:
        flash(e, 'error')
        print(e)

    return render_template('file.html', 
                           form=search_form if is_table else file_form, 
                           is_table=is_table,
                           table=table,
                           action=action)

#########################################
###          REPORT routes            ###
#########################################
@file_blueprint.route('/report', methods=['GET'])
@file_blueprint.route('/report/search', methods=['POST'])
@file_blueprint.route('/report/<int:page>/', methods=['GET'])
@file_blueprint.route('/report/<int:page>/<int:item_per_page>', methods=['GET'])
@login_required
def report_index(page=None, item_per_page=None):
    search_form = SearchForm()
    report_form = ReportForm()
    if 'submitter' in [r.name for r in current_user.roles] and len(current_user.roles) == 1:
        flash('This request is not allowed.', 'error')
        if request.referrer:
            return redirect(request.referrer)
        else:
            return redirect(url_for('user.index'))
        
    # format of message and error
    # {'<key>': ['<message1>','<message2>'...]}
    message = {}
    errors = {}
    table = None
    reports = None
    if request.method == 'GET':
        if page == None and item_per_page == None:
            search_form.search.data = '' 
            session['report_search'] = search_form.search.data
            search_form.item_per_page.data = 5
            session['report_item_per_page'] = search_form.item_per_page.data
            
        
        if page == None:
            page = 1
        
        if item_per_page == None:
            item_per_page = 5
        else:
            search_form.item_per_page.data = item_per_page
            session['report_item_per_page'] = item_per_page

        if 'report_search' in session:
            search_form.search.data = session['report_search']           
        
        if 'report_item_per_page' in session:
            search_form.item_per_page.data = int(session['report_item_per_page'])
        # else:
        #     search_form.item_per_page.data = 5

        # search for reports
        reports = search('reports', search_form, page)       
        

    elif request.method == 'POST':
        if type(page) == str:
            page = int(page)
        if page == None:
            page = 1
        search_form = SearchForm(request.form)
        if not search_form.validate():
            return render_template('report.html',
                               form=report_form,
                               errors=search_form.errors)
        session['report_search'] = search_form.search.data
        session['report_item_per_page'] = int(search_form.item_per_page.data)
        search_form.item_per_page.data = session['report_item_per_page']
        # search for reports
        reports = search('reports', search_form, page)       

    else:
        return    
        
    return render_template('report.html', 
                           form=search_form,
                           table=reports, 
                           is_table=True,
                           available_services=AVAILABLE_SERVICES,
                           action='show',
                           message=message,
                           errors=errors)


@file_blueprint.route('/report/ownership/<int:id>', methods=['GET'])
@login_required
def report_ownership(id):
    report_form = ReportForm()
    if id == None:
        flash('This request is not allowed.', 'error')
        if request.referrer:
            return redirect(request.referrer)
        else:
            return redirect(url_for('user.index'))
    
    if 'submitter' in [r.name for r in current_user.roles] and len(current_user.roles) == 1:
        flash('You do not have permission on this report.', 'error')
        return redirect(url_for('user.index'))
    
    report = Report.query.filter_by(id=id).first()
    report.owned_by = current_user.id
    db.session.add(report)
    db.session.commit()

    return redirect(url_for('file.report', action='edit', id=id))
    


                      
@file_blueprint.route('/report/<regex("view|edit|download|search"):action>/<int:id>', methods=['GET'])
@login_required
# @role_required(role=['admin','reporter'])
def report(action, id):
    report_form = ReportForm()
    service = Service.query.filter_by(name='Report').first()
    report = Report.query.filter_by(id=id, service_id=service.id).first()
    content = Skittish(json.loads(report.content))
    messages = {}
    read_only = False
    if not report:
        return render_template('report.html',
                               form=report_form,
                               errors={'report_id': ['No report found for ReportID: {0}'.format(id)]})
    
    if 'submitter' in [r.name for r in current_user.roles] and len(current_user.roles) == 1:
        read_only = True
    
    try:
        match action:
            case 'download':
                ret, pdf_link = save_to_pdf(id)
                if ret:
                    flash(Markup('The PDF report is ready. Please \
                                 <a href="{0}" class="alert-link">click here</a> \
                                 to download.'.format(pdf_link)), 'success')
                else:
                    flash('ERROR: Failed to generated PDF report.', 'error')

            case _:
                if action != 'view' and read_only:
                    flash('You do not have permission to edit this report.', 'error')
                    return redirect(url_for('file.index'))


        # this is to make sure that the ReportForm 
        # will still display the current view    
        report_form.id.data = report.id
        report_form.sha256.data = report.sha256
        report_form.title.data = content.title
        report_form.content.data = content.content
        report_form.is_published.data = content.is_published
        # report_form.created_date.data = report.created_date.strftime("%d-%m-%Y %H:%M:%S") if report.created_date else ''
        # report_form.modified_date.data = report.modified_date.strftime("%d-%m-%Y %H:%M:%S") if report.modified_date else ''
        # report_form.file_id.data = report.file_id
        # file = File.query.filter_by(id=report.file_id).first()

        messages={'success': ['Report for {0}'.format(report.sha256)]}
        if not read_only:
            flash('{0} - Report for {1}'.format(action, report.sha256), 'warning')

    except Exception as e:
        flash('{0} - {1}'.format(action, e), 'error')
        print(e)

    return render_template('report.html',
                           form=report_form,
                           action=action,
                           messages=messages,
                           read_only=read_only
                           )


@file_blueprint.route('/report/<regex("save"):action>/<int:id>', methods=['POST'])
@login_required
@role_required(role=['admin','reporter'])
def report_post(action, id):
    report_form = ReportForm(request.form)
    # checkbox/switch - is_published doesn't exist in request.form when turned off

    content = Skittish()
    if not report_form.validate():
        return render_template('report.html',
                               form=report_form,
                               action=action,
                               read_only=False,
                               errors=report_form.errors)
    try:
        # continue processing POST data
        service = Service.query.filter_by(name='Report').first()
        match action:
            case 'save':
                report = Report.query.filter_by(id=id, service_id=service.id).first()
                if not report:
                    return render_template('report.html',
                                form=report_form,
                                action=action,
                                errors={'report_id': ['No report found for ReportID: {0}'.format(id)]})
                else:
                    content.title = report_form.title.data
                    content.content = report_form.content.data
                    content.is_published = report_form.is_published.data
                    report.content = json.dumps(content)
                    report.owned_by = current_user.id
                    db.session.add(report)
                    db.session.commit()
                    # file = File.query.options(load_only(File.sha256)
                    #                           ).filter_by(id=report.file_id).first()
                    flash('{0} - changes on report for {1} has been saved.'.format(action, report.sha256), 'success')
        
        # make sure to fill ReportForm with the current ID
        report_form.id.data = id

    except Exception as e:
        flash('Error: {0}'.format(e), 'error')
        print(e)
                
    
    return render_template('report.html',
                           form=report_form,
                           action=action,
                           read_only=False
                           )
    
