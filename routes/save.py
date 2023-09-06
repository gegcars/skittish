import pdfkit
import os
import json
from flask import render_template, request
from ..models import Report, File
from ..forms import ReportForm
from .. import Skittish, DOWNLOAD_DIR



def save_to_pdf(report_id):
    html = ''
    ret = False
    download_path = '' 
    content = ''
    try:
        report = Report.query.filter_by(id=report_id).first()
        content = Skittish(json.loads(report.content))
        html = render_template(
                    'to_pdf.html',
                    title=content.title,
                    skittish_domain='http://'+request.host,
                    hash=report.sha256,
                    content=content.content
                )
        options = {
            'page-size': 'Letter',
            'margin-top': '0.7in',
            'margin-right': '0.7in',
            'margin-bottom': '0.7in',
            'margin-left': '0.7in',
            'encoding': "UTF-8",
            "enable-local-file-access": ""
        }
        download_path = os.path.join(DOWNLOAD_DIR, report.sha256+'.pdf')
        pdfkit.from_string(html, download_path, options=options)
        ret = True

    except Exception as e:
        print(e)
    
    return ret, '/download/{0}.pdf'.format(report.sha256)