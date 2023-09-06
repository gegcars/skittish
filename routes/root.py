from flask import Blueprint, render_template, flash, redirect, url_for, send_file
from flask_login import login_required, logout_user
from .. import DOWNLOAD_DIR
import os



root_blueprint = Blueprint('root', __name__)



@root_blueprint.route('/')
def index():
    return render_template('index.html')


@root_blueprint.route('/download/<regex("[0-9a-fA-F]{64}\.pdf"):hash_report>')
def download_report(hash_report):
    return send_file(
            os.path.join(DOWNLOAD_DIR, '{0}'.format(hash_report)),
            as_attachment=True,
            download_name=hash_report)


@root_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Successfully logged out.', 'message')
    return redirect(url_for('root.index'))