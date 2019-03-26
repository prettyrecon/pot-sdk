#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod: Rest Clinet for Parrot's Block
====================================
.. module author:: 임덕규 <hong18s@gmail.com>
.. note:: MIT License
"""


from alabs.pam.variable_manager.rest import RestClient, \
    REST_API_NAME, REST_API_VERSION, REST_API_PREFIX
import json

class VariableManagerAPI:
    # ==========================================================================
    def __init__(self, ip="127.0.0.1", port="5000"):
        self.rc_api = RestClient(ip, port,"foos",
            # "127.0.0.1", "38800", 'foos',
            url_prefix=REST_API_PREFIX,
            api_name=REST_API_NAME,
            api_version=REST_API_VERSION)

    def post(self, _type="scenarios", name=None, value:dict=None):
        # self.rc_api.set_api_url('mouse', _type)
        rc, rj = self.rc_api.update("metadata.name::=%s" % name, value)
        if not (rc == 200 and rj['success']):
            return False
        return True

