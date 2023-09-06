from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_login import UserMixin
from sqlalchemy import func
from .helpers import generate_hash
import json


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(300), unique=True, index=True)
    name = db.Column(db.String(300), nullable=False)
    # avatar = db.Column(db.String(1024*1000))
    is_active = db.Column(db.Boolean(), default=True)
    password = db.Column(db.String(300), nullable=False)
    # Define the relationship to Role via UserRoles
    roles = db.relationship('Role', secondary='user_roles')
    

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    display_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))


class UserRole(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))
    

class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer(), primary_key=True)
    md5 = db.Column(db.String(), unique=True)
    sha1 = db.Column(db.String(), unique=True)
    sha256 = db.Column(db.String(), unique=True)
    sha512 = db.Column(db.String(), unique=True)
    filename = db.Column(db.String())
    filesize = db.Column(db.Integer())
    data = db.Column(db.LargeBinary(), nullable=False)
    upload_date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    services = db.relationship('Service', secondary='file_services')


class FileService(db.Model):
    __tablename__ = 'file_services'
    id = db.Column(db.Integer(), primary_key=True)
    service_id = db.Column(db.Integer(), db.ForeignKey('services.id', ondelete='CASCADE'))
    file_id = db.Column(db.Integer(), db.ForeignKey('files.id', ondelete='CASCADE'))


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(255))


# ------- Service Models --------
class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer(), primary_key=True)
    service_id = db.Column(db.Integer(), db.ForeignKey('services.id'), index=True, nullable=False)
    sha256 = db.Column(db.String(), unique=True)
    file_id = db.Column(db.Integer(), db.ForeignKey('files.id'), nullable=False)
    # title = db.Column(db.String())
    content = db.Column(db.String())
    created_date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    modified_date = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    # is_published = db.Column(db.Boolean, default=False, nullable=False)
    requested_by = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    owned_by = db.Column(db.Integer(), db.ForeignKey('users.id'))


app = Flask(__name__)

# Create Database file
import os
package_dir = os.path.abspath(os.path.dirname(__file__))
dbfilepath = os.path.join(package_dir,'db'+os.path.sep+'db.sqlite')

import secrets
app.secret_key = secrets.token_urlsafe(64)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfilepath

db.init_app(app)
with app.app_context():
    # Create Tables from Models
    db.create_all()
    # create Roles - Admin, Reporter and Submitter
    admin_role = Role.query.filter_by(name='admin').first()
    reporter_role = Role.query.filter_by(name='reporter').first()
    submitter_role = Role.query.filter_by(name='submitter').first()

    if not admin_role:
        name = 'admin'
        admin_role = Role(
            name=name,
            display_name=name.capitalize(),
            description=None
        )
        db.session.add(admin_role)

    if not reporter_role:
        name = 'reporter'
        reporter_role = Role(
            name=name,
            display_name=name.capitalize(),
            description=None
        )
        db.session.add(reporter_role)
        
    if not submitter_role:
        name = 'submitter'
        submitter_role = Role(
            name=name,
            display_name=name.capitalize(),
            description=None
        )
        db.session.add(submitter_role)

    # commit changes
    db.session.commit()

    # Create user accounts
    if not User.query.filter_by(email='admin@skittish.flask').first():
        # create Admin account
        u = User(
            email='admin@skittish.flask',
            name='admin',
            password=generate_hash(b'admin@password')
        )
        u.roles.append(admin_role)
        u.roles.append(reporter_role)
        u.roles.append(submitter_role)
        db.session.add(u)
        db.session.commit()

    
    user1 = User.query.filter_by(email='analyst1@skittish.flask').first()
    if not user1:
        user1 = User(
            email='analyst1@skittish.flask',
            name='analyst1',
            password=generate_hash(b'analyst1')
        )
        user1.roles.append(admin_role)
        user1.roles.append(reporter_role)
        user1.roles.append(submitter_role)
        db.session.add(user1)
        db.session.commit()

    user2 = User.query.filter_by(email='analyst2@skittish.flask').first()
    if not user2:
        user2 = User(
            email='analyst2@skittish.flask',
            name='analyst2',
            password=generate_hash(b'analyst2')
        )
        user2.roles.append(reporter_role)
        user2.roles.append(submitter_role)
        db.session.add(user2)
        db.session.commit()
    
    user3 = User.query.filter_by(email='analyst3@skittish.flask').first()
    if not user3:
        user3 = User(
            email='analyst3@skittish.flask',
            name='analyst3',
            password=generate_hash(b'analyst3')
        )
        user3.roles.append(reporter_role)
        db.session.add(user3)
        db.session.commit()
    
    user4 = User.query.filter_by(email='analyst4@skittish.flask').first()
    if not user4:
        user4 = User(
            email='analyst4@skittish.flask',
            name='analyst4',
            password=generate_hash(b'analyst4')
        )
        user4.roles.append(submitter_role)
        db.session.add(user4)
        db.session.commit()

    # Check for Services
    report_service = Service.query.filter_by(name="Report").first()
    if not report_service:
        report_service = Service(
            name='Report',
            description='Service for report creation.'
        )
        db.session.add(report_service)
    scanner_service = Service.query.filter_by(name="Scanner").first()
    if not scanner_service:
        report_service = Service(
            name='Scanner',
            description='Service for scanner information.'
        )
        db.session.add(report_service)
    # add service checking here
    # <TO-DO>
    
    # commit changes
    db.session.commit()

    # Create File and draft Report for each file created
    users = [user1, user2, user3, user4]
    contents = [
        "This is the first awesome hash file from ",
        "This is the second awesome hash file from ",
        "This is the third awesome hash file from ",
        "This is the fourth awesome hash file from "
    ]
    report_sample_content = ''
    with open(os.path.join(app.root_path,'report_example.rst'),'rb') as report_content:
        report_sample_content = report_content.read()

    for user in users:
        for data in contents:
            file = File.query.filter_by(sha256=generate_hash(('{0}{1}'.format(data, user.name)).encode('utf-8'))).first()
            if not file:
                file = File(
                    md5=generate_hash(('{0}{1}'.format(data, user.name)).encode('utf-8'), 'md5'),
                    sha1=generate_hash(('{0}{1}'.format(data, user.name)).encode('utf-8'), 'sha1'),
                    sha256=generate_hash(('{0}{1}'.format(data, user.name)).encode('utf-8'), 'sha256'),
                    sha512=generate_hash(('{0}{1}'.format(data, user.name)).encode('utf-8'), 'sha512'),
                    filename='{0}.txt'.format(user.name),
                    filesize=len(data+user.name),
                    data=(data+user.name).encode('utf-8'),
                    user_id=user.id
                )
                # the file needs to be registered, at least for Report service
                report_service = Service.query.filter_by(name='Report').first()
                file.services.append(report_service)
                # add file to db
                db.session.add(file)
                db.session.commit() # to generate file.id before creating report
            # Create report for the file
            report = Report.query.filter_by(file_id=file.id).first()
            if not report:
                report_content = {
                    'title': 'Report for {0}'.format(file.sha256),
                    'content': report_sample_content.decode(),
                    'is_published': False
                }
                report = Report(
                    file_id=file.id,
                    service_id=report_service.id,
                    sha256=file.sha256,
                    content=json.dumps(report_content),
                    requested_by=user.id
                )
                # add report to db
                db.session.add(report)
            # commit changes to db
            db.session.commit()


