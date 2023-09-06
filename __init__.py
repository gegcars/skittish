import secrets
import os
from flask import (
    Flask, session, make_response, 
    render_template, request
)
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from functools import wraps
from .helpers import (
    check_database, get_available_roles, 
    generate_hash, create_admin_account,
    get_available_services
)
from werkzeug.routing import BaseConverter

app = None
db = SQLAlchemy()

package_dir = os.path.abspath(os.path.dirname(__file__))
dbfilepath = os.path.join(package_dir,'db'+os.path.sep+'db.sqlite')
AVAILABLE_ROLES = get_available_roles(dbfilepath)
AVAILABLE_SERVICES = get_available_services(dbfilepath)
DOWNLOAD_DIR = os.path.join(package_dir, 'download')
UPLOAD_DIR = os.path.join(package_dir, 'upload')



class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


class Skittish(dict):
    """ Nested Attribute Dictionary
    A class to convert a nested Dictionary into an object with key-values
    accessible using attribute notation (__classname__.attribute) in addition to
    key notation (Dict["key"]). This class recursively sets Dicts to objects,
    allowing you to get into nested dicts (like: __classname__.attr.attr)
    """

    def __init__(self, mapping=None):
        super(Skittish, self).__init__()
        if mapping is not None:
            for key, value in mapping.items():
                self.__setitem__(key, value)

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = Skittish(value)
        super(Skittish, self).__setitem__(key, value)
        self.__dict__[key] = value  # for code completion in editors

    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError(item)

    __setattr__ = __setitem__


def role_required(role=["ANY"]):
    """
    https://stackoverflow.com/questions/63549476/how-to-implement-role-based-access-control-in-flask
    see: https://flask.palletsprojects.com/en/2.1.x/patterns/viewdecorators/
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            flag = True
            error = {
                'status' : '403 Forbidden',
                'message': 'Permission denied',
                'path' : request.path
            }
            for r in role:
                if r in [r.name for r in current_user.roles]:
                    flag = True
                    break
                else:
                    flag = False

            if not flag:
                resp = make_response(render_template('error.html', error=error), 403)
                return resp
                        
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.url_map.converters['regex'] = RegexConverter
    app.secret_key = secrets.token_urlsafe(64)
    app.config['SESSION_PERMANENT'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfilepath
    app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
    # initialize CSRFProtect
    csrf = CSRFProtect()
    csrf.init_app(app)

    # initialize SQLAlchemy for the app
    db.init_app(app)
    from .models import User, Role
    db_details = Skittish({
        'app': app,
        'db': db,
        'dbfilepath': dbfilepath,
        'User': User, # User object
        'Role': Role # Role object
    })    
    # check if users and roles tables are empty
    check_database(db_details)
    # create admin account
    db_admin = db_details
    setattr(db_admin, 'email', 'admin@skittish.flask')
    setattr(db_admin, 'name', 'admin')
    setattr(db_admin, 'password', generate_hash(b'admin@password'))
    create_admin_account(db_admin)

    # once stored, delete Skittish object
    del db_details
    del db_admin

    # initialize Bootstrap
    Bootstrap(app)

    # register Blueprints
    from .routes.root import root_blueprint
    app.register_blueprint(root_blueprint)
    from .routes.login import login_blueprint
    app.register_blueprint(login_blueprint)
    from .routes.signup import signup_blueprint
    app.register_blueprint(signup_blueprint)
    from .routes.user import user_blueprint
    app.register_blueprint(user_blueprint)    
    from .routes.role import role_blueprint
    app.register_blueprint(role_blueprint)
    from .routes.file import file_blueprint
    app.register_blueprint(file_blueprint)
    from .services.report import report_blueprint
    app.register_blueprint(report_blueprint)
    # from .routes.admin import admin_blueprint
    # app.register_blueprint(admin_blueprint)
    # from .routes.report import report_blueprint
    # app.register_blueprint(report_blueprint)

    # create the login manager
    login_manager = LoginManager()
    login_manager.login_view = 'login.index'
    login_manager.init_app(app)

    # This is needed when using flask_login
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, 
        # use it in the query for the user to get other details such email and name
        return User.query.get(int(user_id))
    
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html')
    
    return app
    