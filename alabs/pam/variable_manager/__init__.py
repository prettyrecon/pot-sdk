import os

# REST API Port
VM_API_PORT = os.environ.get('VM_API_PORT')

# External Store (Vault)
EXTERNAL_STORE_ADDRESS_PORT = os.environ.get('EXTERNAL_STORE_ADDRESS_PORT')
EXTERNAL_STORE_TOKEN = os.environ.get('EXTERNAL_STORE_TOKEN')
EXTERNAL_STORE_NAME = os.environ.get('EXTERNAL_STORE_NAME') + '/variables'

from alabs.pam.variable_manager.variable_manager import Variables
from alabs.pam.variable_manager.variable_manager import Variables
variables = Variables()
