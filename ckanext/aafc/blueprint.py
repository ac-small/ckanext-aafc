from flask import Blueprint, make_response
import ckanapi_exporter.exporter as exporter
import ckan.plugins.toolkit as tk
from ckan.common import c
from datetime import datetime

aafc = Blueprint('aafc', __name__)

def help_page():
    return tk.render('/home/help.html')

def export():
    '''
    Use ckanapi-exporter to export records into a csv file.
    Columns exported are specified in the /export/export.columns.json file.
    Exported files are labelled with current datetime.
    '''
    csv_bom_header = ('\ufeff')
    data = exporter.export('http://localhost:5000/', '/srv/app/src/ckanext-aafc/ckanext/aafc/export/export_columns.json', str(c.userobj.apikey) , "{'include_private':'True'}")
    csv_content = csv_bom_header + data

    response = make_response(csv_content)
    time = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = ("AAFC-Data-Catalogue-Export " + time + ".csv")
    response.headers['Content-Encoding'] = 'utf-8-sig'
    response.headers['Content-Type'] = 'text/plain; charset=utf-8-sig'
    response.headers["Content-Disposition"] = "attachment; filename=" + filename
    return response

def get_blueprints():
    return [aafc]

aafc.add_url_rule('/help', '/help', view_func=help_page)
aafc.add_url_rule('/export', '/export', view_func=export)

