from sqlalchemy.orm import load_only
from ..models import *
from flask_login import current_user



def search_users(search_form, page=1):
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
        
    else: # else search using the search criteria
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
        
    else: # else search using the search criteria
        results = Role.query.filter((Role.name.ilike("%"+search_data+"%")) | 
                                    (Role.display_name.ilike("%"+search_data+"%")) | 
                                    (Role.description.ilike("%"+search_data+"%"))
                                    ).paginate(page=page,
                                            per_page=search_form.item_per_page.data, 
                                            error_out=True, 
                                            max_per_page=5)
    return results

def search_files(search_form, page, user_id):
    # search users table using email or name
    results = []
    search_data = search_form.search.data
    if not search_data:
        search_data = 'all'
    if search_data.upper() in ['ALL', '*']:
        results = File.query.options(
            load_only(File.id, File.filename, File.sha256, File.user_id, File.upload_date)
            ).filter(File.user_id == user_id).order_by(File.upload_date.desc()
                       ).paginate(page=page, 
                                  per_page=search_form.item_per_page.data, 
                                  error_out=True, 
                                  max_per_page=5)
    
    else: # else search using the search criteria
        results = File.query.options(
            load_only(File.id, File.filename, File.sha256, File.user_id, File.upload_date)
            ).filter(((File.sha256.ilike("%"+search_data+"%"))
                     | (File.filename.ilike("%"+search_data+"%")) 
                     # | (File.description.ilike("%"+search_data+"%"))
                     ) & (File.user_id == user_id)).order_by(File.upload_date.desc()
                                ).paginate(page=page,
                                           per_page=search_form.item_per_page.data, 
                                           error_out=True, 
                                           max_per_page=5)
    if results:
        # change file.user_id with user.email for visual
        for file in results:
            setattr(file, 'user_id', User.query.filter_by(id=file.user_id).first().email)
    
    return results


def search_reports(search_form, page):
    results = []
    search_data = search_form.search.data
    service = Service.query.filter_by(name='Report').first()
    if not search_data:
        search_data = 'all'
    if search_data.upper() in ['ALL', '*']:
        # search for reports that is not owned yet
        results = Report.query.filter_by(
            owned_by=None, service_id=service.id
            ).order_by(Report.created_date.desc()
                       ).paginate(page=page,
                                  per_page=search_form.item_per_page.data, 
                                  error_out=True, 
                                  max_per_page=5)
    
    else:
        results = Report.query.filter_by(owned_by=None, service_id=service.id).filter(
            Report.sha256.ilike("%"+search_data+"%")
            ).paginate(page=page,
                       per_page=search_form.item_per_page.data, 
                       error_out=True, 
                       max_per_page=5)

    # change Requested By user_id by email address
    for report in results:
        setattr(report, 'requested_by', User.query.filter_by(id=report.requested_by).first().email) 

    return results


def search(table_name, search_form, page_num=1):
    results = []
    if table_name == 'users':
        results = search_users(search_form, page_num)
    elif table_name == 'roles':
        results = search_roles(search_form, page_num)
    elif table_name == 'files':
        results = search_files(search_form, page_num, current_user.id)
    elif table_name == 'reports':
        results = search_reports(search_form, page_num)

    return results
