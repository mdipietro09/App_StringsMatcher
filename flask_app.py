###############################################################################
#                            RUN MAIN                                         #
###############################################################################

# setup
## pkg
import flask
import pandas as pd

from model.string_matcher import StringMatcher
from settings import config

## app
app = flask.Flask(__name__, 
				instance_relative_config=True, 
       			template_folder=config.root+'client/templates',
                static_folder=config.root+'client/static')



# main
@app.route("/", methods=['GET','POST'])
def index():
	try:
		if flask.request.method == 'POST':
			## data from client
			app.logger.info(flask.request.files)
			app.logger.info(flask.request.form)
			dtf_lookup = pd.read_excel(flask.request.files["dtf_lookup"])
			dtf_match = pd.read_excel(flask.request.files["dtf_match"])
			threshold = float(flask.request.form["threshold"])
			top = 1 if flask.request.form["top"].strip() == "" else int(flask.request.form["top"])
			app.logger.warning("--- Inputs Received ---")

			## match
			model = StringMatcher(dtf_lookup, dtf_match)
			dtf_out = model.vlookup(threshold=threshold, top=top)
			xlsx_out = model.write_excel(dtf_out)
			return flask.send_file(xlsx_out, attachment_filename='StringsMatcher.xlsx', as_attachment=True)             
		else:
			return flask.render_template("index.html")

	except Exception as e:
		app.logger.error(e)
		flask.abort(500)
    

   
# errors
@app.errorhandler(404)
def page_not_found(e):
    return flask.render_template("errors.html", msg="Page doesn't exist"), 404
    

@app.errorhandler(500)
def internal_server_error(e):
    return flask.render_template('errors.html', msg="Something went terribly wrong"), 500



# run
if __name__ == "__main__":
    app.run(host=config.host, port=config.port, debug=config.debug)