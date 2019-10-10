###############################################################################
#                            RUN MAIN                                         #
###############################################################################

from instance.config.app_settings import *
from instance.config.file_system import *
from app.server import server



app = server.create_app(name=name)

app.run(host=host, port=port, threaded=threaded, debug=debug)