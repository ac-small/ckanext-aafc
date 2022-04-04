from flask import Blueprint
import ckanapi_exporter.exporter as exporter
import ckan.plugins.toolkit as tk
from datetime import datetime
from flask import Response, make_response

aafc = Blueprint('aafc', __name__)

def help_page():
    return tk.render('/home/help.html')

def build_export():
    csv_content = exporter.get_datasets_from_ckan("http://localhost:5000/", apikey="")
    #csv_content="Hello World"
    return csv_content

def export():
    '''
    Use ckanapi-exporter to export records into a csv file.
    Columns exported are specified in the /export/export.columns.json file.
    Exported files are labelled with current datetime.
    '''
    response = make_response(build_export())
    time = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = ("AAFC-Data-Catalogue-Export " + time + ".csv")
    response.headers['Content-Encoding'] = 'utf-8-sig'
    response.headers['Content-Type'] = 'text/plain; charset=utf-8-sig'
    response.headers["Content-Disposition"] = "attachment; filename=" + filename
    #response.write("\xEF\xBB\xBF")
    return response

def get_blueprints():
    return [aafc]

aafc.add_url_rule('/help', '/help', view_func=help_page)
aafc.add_url_rule('/export', '/export', view_func=export)

