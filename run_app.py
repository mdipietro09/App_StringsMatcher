###############################################################################
#                            RUN MAIN                                         #
###############################################################################

from settings import config
from app.server import server



app = server.create_app()

app.run(host=config.host, port=config.port, debug=config.debug)