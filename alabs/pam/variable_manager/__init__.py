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

from alabs.pam.variable_manager.variable_manager import Variables
variables = Variables()

import os
from flask import Flask
from flask_restplus import Api
from alabs.pam.variable_manager.rest.ns_variables import api as ns_variables



REST_API_PREFIX = 'api'
REST_API_VERSION = 'v1.0'
REST_API_NAME = 'var'



################################################################################
WITH_AAA = int(os.environ.get('WITH_AAA', '0'))
if not WITH_AAA:
    print('>>>NO AAA')
else:
    print('>>>WITH AAA')

################################################################################
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

################################################################################


api_port = VM_API_PORT
if not api_port:
    raise RuntimeError('API_PORT environment variable is not set!')
app.run(host="0.0.0.0", port=int(api_port))
