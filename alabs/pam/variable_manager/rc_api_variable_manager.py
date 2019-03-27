#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod: Rest Clinet for Parrot's Block
====================================
.. module author:: 임덕규 <hong18s@gmail.com>
.. note:: MIT License
"""


from alabs.pam.variable_manager.rest import RestClient
from alabs.pam.variable_manager import \
    REST_API_NAME, REST_API_VERSION, REST_API_PREFIX, RequestData, \
    ResponseErrorData


class VariableManagerAPI:
    # ==========================================================================
    def __init__(self, ip="127.0.0.1", port="8011"):
        self.rc_api = RestClient(ip, port, "",
                                 url_prefix=REST_API_PREFIX,
                                 api_version=REST_API_NAME,
                                 api_name=REST_API_VERSION)

    # ==========================================================================
    def create(self, path, value):
        self.rc_api.set_resource('variables')
        data = {"path": path,"value": value}
        data = RequestData(data)
        response = self.rc_api.do_http(
            "POST", self.rc_api.url_path, data, use_param_url=None)
        return response

    # ==========================================================================
    def get(self, path):
        self.rc_api.set_resource('variables')
        data = {"path": path }
        data = RequestData(data)
        response = self.rc_api.do_http(
            "GET", self.rc_api.url_path, data, use_param_url=None)
        return response


    # ==========================================================================
    def convert(self, value):
        self.rc_api.set_resource('convert')
        data = {"value": value }
        data = RequestData(data)
        response = self.rc_api.do_http(
            "GET", self.rc_api.url_path, data, use_param_url=None)
        return response

