################################################################################
__author__ = "Duk Kyu Lim <hong18s@gmail.com>"
__date__ = "2019/03/15"
__version__ = "1.0.0"
__version_info__ = (1, 0, 0)
__license__ = "MIT"


from flask import Flask
from flask_rextx import Api
from .app import api as test_api


################################################################################
def main(api_port=8082, *args):
    app = None
    endpoint ='/%s/%s/%s' % ('api', 'v1.0', 'test')
    try:
        app = Flask(__name__)
        api = Api(
            title='ARGOS BOT-REST-Server',
            version='1.0',
            description='BOT RESTful Server')
        api.add_namespace(test_api, path=endpoint)

        app.logger.info("Start RestAPI from [%s]..." % __name__)
        app.logger.info("End-Point [%s]..." % endpoint)
        api.init_app(app)
    except Exception as err:
        if app and app.logger:
            app.logger.error('Error: %s' % str(err))
        raise
    app.run(host="0.0.0.0", port=int(api_port))
