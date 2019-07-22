#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod: Rest Clinet for Parrot's Block
====================================
.. module author:: 임덕규 <hong18s@gmail.com>
.. note:: MIT License
"""
import json
import urllib.parse
from requests import Response

from alabs.common.util.vvjson import convert_str
from alabs.pam.variable_manager.rest import RestClient
from alabs.pam.variable_manager import \
    REST_API_NAME, REST_API_VERSION, REST_API_PREFIX, RequestData
#     ResponseErrorData
from alabs.common.util.vvlogger import get_logger


################################################################################
def get_response_data(resp: Response):
    text = resp.text
    if not text:
        text = 'null'
    return resp.status_code, convert_str(json.loads(text))


################################################################################
class VariableManagerAPI:
    # ==========================================================================
    def __init__(self, ip="127.0.0.1", port="8012", pid=0, logger=None):
        self.rc_api = RestClient(ip, port, "",
                                 url_prefix=REST_API_PREFIX,
                                 api_version=REST_API_NAME,
                                 api_name=REST_API_VERSION)

        self._pid = str(pid)
        self.logger = None
        if logger is None:
            logger = get_logger("variable_manager_api.log")
        self.logger = logger

    # ==========================================================================
    def create(self, path, value):
        try:
            self.logger.info("{}")
            self.rc_api.set_resource('variables')
            data = {"path": path, "value": value, "name": str(self._pid)}
            data = RequestData(data)
            response = self.rc_api.do_http(
                "POST", self.rc_api.url_path, data, use_param_url=None)
            return get_response_data(response)
        except Exception as e:
            self.logger.info("ERROR: {}".format(str(e)))
            raise Exception

    # ==========================================================================
    def get(self, path):
        self.rc_api.set_resource('variables')
        query = {"path": path, "name": self._pid}
        self.rc_api.url_path += '?' + urllib.parse.urlencode(query)
        response = self.rc_api.do_http("GET", self.rc_api.url_path)
        return get_response_data(response)

    # ==========================================================================
    def convert(self, value):
        self.rc_api.set_resource('convert')
        data = {"value": value, "name": str(self._pid)}
        data = RequestData(data)
        response = self.rc_api.do_http(
            "POST", self.rc_api.url_path, data, use_param_url=None)
        return get_response_data(response)

