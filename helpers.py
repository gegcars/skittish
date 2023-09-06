
import datetime
import os
import hashlib
import sqlite3
from colorama import Fore, Style


def log_print(message):
    print(
        Fore.BLUE + f"[{datetime.date.today()} " +
        Fore.CYAN + f"{datetime.datetime.now().strftime('%H:%M:%S')}] " +
        Fore.GREEN + f"{message}"
    )
    print(Style.RESET_ALL)


def get_available_roles(dbfilepath):
    available_roles = []
    try:
        r = """SELECT name FROM roles;"""
        conn = sqlite3.connect(dbfilepath)
        cursor = conn.cursor()
        cursor.execute(r)
        available_roles = [n[0] for n in cursor]
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(e)

    return available_roles


def get_available_services(dbfilepath):
    available_services = []
    try:
        r = """SELECT name FROM services;"""
        conn = sqlite3.connect(dbfilepath)
        cursor = conn.cursor()
        cursor.execute(r)
        available_services = [n[0] for n in cursor]
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(e)

    return available_services


def check_database(details):
    # make sure the database folder exist
    match os.path.exists(os.path.dirname(details.dbfilepath)):
        case False:
            os.mkdir(os.path.dirname(details.dbfilepath))
    # Create the Tables from Models
    with details.app.app_context():
        details.db.create_all() # this will also create the database file
        

def create_admin_account(details):
    with details.app.app_context():
        u = r = None
        if not details.User.query.filter_by(email='admin@skittish.flask').first():
            # create Admin account
            u = details.User(
                email='admin@skittish.flask',
                name='admin',
                password=generate_hash(b'admin@skittish')
            )
            # check if Role Admin already exist
            if not details.Role.query.filter_by(name='admin').first():
                r = details.Role(
                    name='admin',
                    description='User, Role and Content management.'
                )
                # commit changes for Admin role
                details.db.session.add(r)
                details.db.session.commit()
                
            # commit changes for admin user
            u.roles.append(r)
            details.db.session.add(u)
            details.db.session.commit()


def generate_hash(password, method='sha256'):
    hasher = None
    if method.upper() == 'SHA256':
        hasher = hashlib.sha256()
    elif method.upper() == 'SHA1':
        hasher = hashlib.sha1()
    elif method.upper() == 'MD5':
        hasher = hashlib.md5()
    elif method.upper() == 'SHA512':
        hasher = hashlib.sha512()
    hasher.update(password)
    hasher.digest()
    
    return hasher.hexdigest()


def check_password_hash(password_hash, password, method='sha256'):
    is_match = False
    hashed_password = generate_hash(password)
    if hashed_password.upper() == password_hash.upper():
        is_match = True
    
    return is_match



