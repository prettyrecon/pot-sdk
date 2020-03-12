import os
################################################################################
__author__ = "Duk Kyu Lim <hong18s@gmail.com>"
__date__ = "2019/03/15"
__version__ = "1.0.0"
__version_info__ = (1, 0, 0)
__license__ = "MIT"



# REST API Port
VM_API_PORT = os.environ.get('VM_API_PORT', '8011')

# External Store (Vault)
EXTERNAL_STORE_ADDRESS_PORT = os.environ.get('EXTERNAL_STORE_ADDRESS_PORT')
EXTERNAL_STORE_TOKEN = os.environ.get('EXTERNAL_STORE_TOKEN')
EXTERNAL_STORE_NAME = os.environ.get('EXTERNAL_STORE_NAME', '') + '/variables'


################################################################################
class RequestData(dict):
    def __init__(self, data):
        dict.__init__(self)
        self['data'] = data




################################################################################
# class ResponseData(dict):
#     def __init__(self, resp:Response):
#         dict.__init__(self)
#         self['code'] = resp.status_code
#         self['data'] = convert_str(json.loads(resp.text))

###############################################################################
class ResponseErrorData(dict):
    def __init__(self, data):
        dict.__init__(self)
        self['message'] = data



from alabs.pam.variable_manager.variable_manager import Variables
from alabs.pam.variable_manager.variable_manager import number_format
variables = Variables(base_index=1)

import os
from flask import Flask
from flask_restx import Api
from alabs.pam.variable_manager.rest.ns_variables import api as ns_variables



REST_API_PREFIX = 'api'
REST_API_VERSION = 'v1.0'
REST_API_NAME = 'var'


################################################################################
def main(*args):
    app = None
    try:
        # Flask app
        app = Flask(__name__)
        api = Api(
            title='ARGOS VARIABLES-REST-Server',
            version='1.0',
            description='VARIABLES RESTful Server',
        )
        # TODO: 환경변수로 버전 정보를 가지고 있어야 함
        api.add_namespace(ns_variables, path='/%s/%s/%s' % (REST_API_PREFIX,
                                                            REST_API_VERSION,
                                                            REST_API_NAME))

        app.logger.info("Start RestAPI from [%s]..." % __name__)
        api.init_app(app)
    except Exception as err:
        if app and app.logger:
            app.logger.error('Error: %s' % str(err))
        raise

    api_port = VM_API_PORT
    if not api_port:
        raise RuntimeError('API_PORT environment variable is not set!')
    app.run(host="0.0.0.0", port=int(api_port), debug=True)

################################################################################

