from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields import *
from wtforms.validators import DataRequired, Length, EqualTo
from . import AVAILABLE_ROLES, AVAILABLE_SERVICES


class LoginForm(FlaskForm):
    email = EmailField('Email Address', validators=[DataRequired(), Length(1, 300)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 300)])
    is_active = BooleanField('Is Active')
    remember_me = BooleanField('Remember me')
    submit = SubmitField()


class SignUpForm(FlaskForm):
    email = EmailField('Email Address', validators=[DataRequired(), Length(1, 300)])
    name = StringField('Name', validators=[DataRequired(), Length(1, 300)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 300), 
                            EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm password')
    submit = SubmitField()


class UserForm(FlaskForm):
    id = IntegerField('Id')
    email = EmailField('Email Address', validators=[DataRequired(), Length(1, 300)])
    name = StringField('Name', validators=[DataRequired(), Length(1, 300)])
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password')
    role = SelectMultipleField(choices=AVAILABLE_ROLES, validators=[DataRequired()])
    submit = SubmitField()


class RoleForm(FlaskForm):
    id = IntegerField('Id')
    name = StringField('Name', validators=[DataRequired(), Length(1, 300)])
    display_name = StringField('Display Name', validators=[DataRequired(), Length(1, 300)])
    description = StringField('Description', validators=[DataRequired(), Length(1, 300)])
    submit = SubmitField()


class FileForm(FlaskForm):
    id = IntegerField('Id')
    filename = StringField('Filename', validators=[DataRequired()])
    filesize = IntegerField('Filesize', validators=[DataRequired()])
    md5 = StringField('MD5', validators=[DataRequired()])
    sha1 = StringField('SHA1', validators=[DataRequired()])
    sha256 = StringField('SHA256', validators=[DataRequired()])
    sha512 = StringField('SHA512', validators=[DataRequired()])
    file_services = StringField('Services')
    

class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired(), Length(1, 300)])
    item_per_page = SelectField(choices=[n+1 for n in range(5)], validators=[DataRequired()])
    submit = SubmitField()


class ReportForm(FlaskForm):
    id = IntegerField('Id')
    title = StringField('Title', validators=[DataRequired(), Length(10, 300)])
    content = StringField('Content', validators=[DataRequired()])
    created_date = DateTimeField('Date Created')
    modified_date = DateTimeField('Date Modified')
    is_published = BooleanField('Is Published')
    file_id = IntegerField('File Id')
    requested_by = IntegerField('Requested By')
    owned_by = IntegerField('Owned By')
    sha256 = StringField('SHA256')
    submit = SubmitField()