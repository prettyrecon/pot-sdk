################################################################################
__author__ = "Duk Kyu Lim <hong18s@gmail.com>"
__date__ = "2019/03/15"
__version__ = "1.0.0"
__version_info__ = (1, 0, 0)
__license__ = "MIT"


from flask import Flask
from flask_restplus import Api
from alabs.pam.la.bot.app.status import api as api_status


################################################################################
def main(api_port=8082, *args):
    app = None
    try:
        # Flask app
        app = Flask(__name__)
        api = Api(
            title='ARGOS BOT-REST-Server',
            version='1.0',
            description='BOT RESTful Server',
        )
        api.add_namespace(api_status, path='/%s/%s/%s' % ('api', 'v1.0', 'pam'))

        app.logger.info("Start RestAPI from [%s]..." % __name__)
        api.init_app(app)
    except Exception as err:
        if app and app.logger:
            app.logger.error('Error: %s' % str(err))
        raise
    app.run(host="0.0.0.0", port=int(api_port))


