#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod: Rest Clinet for Parrot's Block
====================================
.. module author:: 임덕규 <hong18s@gmail.com>
.. note:: MIT License
"""
import os
import json
import traceback
import urllib.parse
from urllib3.exceptions import MaxRetryError
from requests import Response

from alabs.pam.conf import get_conf
from alabs.common.util.vvjson import convert_str
from alabs.pam.variable_manager.rest import RestClient
from alabs.pam.variable_manager import \
    REST_API_NAME, REST_API_VERSION, REST_API_PREFIX, RequestData
#     ResponseErrorData
from alabs.common.util.vvlogger import get_logger, StructureLogFormat, \
    LogMessageHelper
from alabs.common.util.vvtest import captured_output
from alabs.pam.conf import get_conf




################################################################################
class VariableManagerAPI:
    # ==========================================================================
    def __init__(self, ip=None, port=None, pid=0, logger=None):
        if logger is None:
            logger = get_logger(get_conf().get('/PATH/PAM_LOG'))
        self.logger = logger
        self.log_msg = LogMessageHelper()

        conf = get_conf(self.logger)
        if not ip:
            ip = conf.get("/MANAGER/VARIABLE_MANAGER_IP")
        if not port:
            port = conf.get("/MANAGER/VARIABLE_MANAGER_PORT")

        self.logger.info(self.log_msg.format(
            'Connecting to the variable manager.'))
        self.logger.debug(StructureLogFormat(
            VAR_MGR_IP=ip, VAR_MGR_PORT=port,
            VAR_MGR_END_POINT=''.format('/'.join(
                [REST_API_PREFIX, REST_API_VERSION, REST_API_NAME]))))

        self.rc_api = RestClient(ip, port, "",
                                 url_prefix=REST_API_PREFIX,
                                 api_version=REST_API_NAME,
                                 api_name=REST_API_VERSION)
        self._pid = str(pid)

    # ==========================================================================
    def create(self, path, value):
        try:
            self.logger.info(self.log_msg.format(
                'Requesting to create a variable.'))
            self.rc_api.set_resource('variables')
            data = {"path": path, "value": value, "name": str(self._pid)}
            data = RequestData(data)
            self.logger.debug(StructureLogFormat(
                REQUEST_METHOD="POST",
                REQUEST_URL=self.rc_api.url_path,
                REQUEST_DATA=dict(data)))

            response = self.rc_api.do_http(
                "POST", self.rc_api.url_path, data, use_param_url=None)

            return self.get_response_data(response)
        except MaxRetryError as e:
            self.logger.error(str(e))
        except Exception as e:
            self.logger.error(str(e))
            raise Exception

    # ==========================================================================
    def get(self, path):
        self.logger.info(self.log_msg.format('Requesting to get a variable.'))
        try:
            self.rc_api.set_resource('variables')
            query = {"path": path, "name": self._pid}
            self.rc_api.url_path += '?' + urllib.parse.urlencode(query)
            self.logger.debug(StructureLogFormat(
                REQUEST_METHOD="POST",
                REQUEST_URL=self.rc_api.url_path))

            response = self.rc_api.do_http("GET", self.rc_api.url_path)

            return self.get_response_data(response)
        except MaxRetryError as e:
            self.logger.error(str(e))
        except Exception as e:
            self.logger.error(str(e))
            raise Exception

    # ==========================================================================
    def convert(self, value):
        self.rc_api.set_resource('convert')
        data = {"value": value, "name": str(self._pid)}
        data = RequestData(data)
        response = self.rc_api.do_http(
            "POST", self.rc_api.url_path, data, use_param_url=None)
        return self.get_response_data(response)

    # ==========================================================================
    def get_response_data(self, resp: Response):
        text = resp.text
        if not text:
            text = 'null'
        code, data = resp.status_code, convert_str(json.loads(text))
        self.logger.info(self.log_msg.format(
            'Received the response from variable manager.'))
        if 200 < code and not 500 < code:
            self.logger.warn(self.log_msg.format('Failed to get the data.'))
            self.logger.debug(
                StructureLogFormat(RESPONSE_CODE=code, RESPONSE_DATA=data))
        else:
            self.logger.debug(
                StructureLogFormat(RESPONSE_CODE=code, RESPONSE_DATA=data))
        return code, data
