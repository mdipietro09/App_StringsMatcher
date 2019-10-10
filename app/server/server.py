###############################################################################
#                                MAIN                                         #
###############################################################################

import flask
import pandas as pd

from model.strings_matcher import strings_matcher

from instance.config.file_system import *



'''
'''
def create_app(name=None):
    ## app object
    name = name if name is not None else __name__
    app = flask.Flask(name, instance_relative_config=True, 
                      template_folder=dirpath+'app/client/templates',
                      static_folder=dirpath+'app/client/static')
        
    
    ## api
    @app.route('/ping', methods=["GET"])
    def ping():
        return 'pong'
    
    @app.route("/", methods=['GET', 'POST'])
    def index():
        try:
            if flask.request.method == 'POST':
                ## data from client
                dtf_lookup = pd.read_excel(flask.request.files["dtf_lookup"])
                dtf_match = pd.read_excel(flask.request.files["dtf_match"])
                top = int(flask.request.form["top"])
                threshold = float(flask.request.form["threshold"])
                ## match
                model = strings_matcher(dtf_lookup, dtf_match)
                dtf_out = model.vlookup(threshold=threshold, top=top)
                xlsx_out = model.write_excel(dtf_out)
                return flask.send_file(xlsx_out, attachment_filename='StringsMatcher.xlsx', as_attachment=True)             
            else:
                return flask.render_template("index.html")
        except Exception as e:
            app.logger.error(e)
            flask.abort(500)
        
    
    ## errors
    @app.errorhandler(404)
    def page_not_found(e):
        return flask.render_template("errors.html", msg="Page doesn't exist"), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return flask.render_template('errors.html', msg="Something went terribly wrong"), 500
    
    
    return app