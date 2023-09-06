from sqlalchemy import func
from flask_login import UserMixin
from . import db


class User(db.Model, UserMixin):
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
    

