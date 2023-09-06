from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from ..models import File, Report
from .. import Skittish
import json

report_blueprint = Blueprint('report', __name__)


# @report_blueprint.route('/service/report/<regex("[0-9a-fA-F]{32,}"):hash>', methods=["GET"])
@report_blueprint.route('/service/report/<hash>', methods=["GET"])
@login_required
def report(hash):
    report = None
    file = None
    if len(hash) == 32:
        file = File.query.filter_by(md5=hash).first()
    elif len(hash) == 40:
        file = File.query.filter_by(sha1=hash).first()
    elif len(hash) == 64:
        file = File.query.filter_by(sha256=hash).first()
    elif len(hash) == 128:
        file = File.query.filter_by(sha512=hash).first()
    else:
        return jsonify({'report': {}, 'message':'', 'error':'Unsupported hash {0}'.format(hash)})
    
    # get the report of the given hash
    report_obj = Skittish({
        'report': {
            'id': '',
            'title': '',
            'content': '',
            'created_date': '',
            'modified_date': ''
        },
        'file': {
            'id': '',
            'filename': '',
            'filesize': '',
            'md5': '',
            'sha1': '',
            'sha256': '',
            'sha512': '',
            'upload_date': ''
        },
        'message': '',
        'error': '',
        'read_only': 1
    })

    if 'submitter' in [r.name for r in current_user.roles] and len(current_user.roles) == 1:
        report = Report.query.filter_by(file_id=file.id).first()
        content = Skittish(json.loads(report.content))
        if not content.is_published:
            return jsonify({
                'report': {},
                'message': '',
                'error': 'No published report yet for {0}'.format(hash)
            })
    else:
        report_obj.read_only = 0
    
    report = Report.query.filter_by(file_id=file.id).first()
    content = Skittish(json.loads(report.content))
    report_obj.report.id = report.id
    report_obj.report.title = content.title
    report_obj.report.content = content.content
    report_obj.report.created_date = report.created_date.strftime("%d-%m-%Y %H:%M:%S") if report.created_date else ''
    report_obj.report.modified_date = report.modified_date.strftime("%d-%m-%Y %H:%M:%S") if report.modified_date else ''
    current_user_roles = [r.name for r in current_user.roles]
    if 'admin' in current_user_roles or 'reporter' in current_user_roles:
        report_obj.report.is_published = content.is_published
    report_obj.file.id = file.id
    report_obj.file.filename = file.filename
    report_obj.file.filesize = file.filesize
    report_obj.file.md5 = file.md5
    report_obj.file.sha1 = file.sha1
    report_obj.file.sha256 = file.sha256
    report_obj.file.sha512 = file.sha512
    report_obj.file.upload_date = file.upload_date.strftime("%d-%m-%Y %H:%M:%S") if file.upload_date else ''
    report_obj.message = 'Report for {0}'.format(hash)
    

    return report_obj

    
    # return jsonify({
    #         'report': {
    #             'id': report.id,
    #             'title': report.title,
    #             'content': report.content,
    #             'created_date': report.created_date.strftime("%d-%m-%Y %H:%M:%S") if report.created_date else '',
    #             'modified_date': report.modified_date.strftime("%d-%m-%Y %H:%M:%S") if report.modified_date else ''
    #         },
    #         'file': {
    #             'id': file.id,
    #             'filename': file.filename,
    #             'filesize': file.filesize,
    #             'md5': file.md5,
    #             'sha1': file.sha1,
    #             'sha256': file.sha256,
    #             'sha512': file.sha512,
    #             'upload_date': file.upload_date.strftime("%d-%m-%Y %H:%M:%S") if file.upload_date else ''
    #         },
    #         'message': 'Successfully fetched report for {0}'.format(hash),
    #         'error': ''
    #     })
