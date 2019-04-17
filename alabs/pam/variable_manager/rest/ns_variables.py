#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod:`vivans.rest.ns_file` rest service using Flask-RESTful and
    file BackEnd
====================================
.. moduleauthor:: 임덕규 <hong18s@gmail.com>
.. note:: MIT
"""

# 설명
# =====

# 관련 작업자
# ===========
#
# 본 모듈은 다음과 같은 사람들이 관여했습니다:
#  * 임덕규
#
# 작업일지
# --------
#
# 다음과 같은 작업 사항이 있었습니다:
#  * [2018/04/11]
#     - 본 모듈 작업 시작
################################################################################

# noinspection PyProtectedMember
from flask_restplus import Namespace, Resource, reqparse
from flask import request
from alabs.pam.variable_manager import variables
from alabs.pam.variable_manager import ResponseData, \
    ResponseErrorData


################################################################################
__author__ = "Duk Kyu Lim <mcchae@gmail.com>"
__date__ = "2018/04/11"
__version__ = "1.18.0411"
__version_info__ = (1, 18, 411)
__license__ = "MIT"

################################################################################
api = Namespace('ns_variables', description='Variables Manager API')


################################################################################
# noinspection PyMethodMayBeStatic
@api.route('/ping')
class Ping(Resource):
    # ==========================================================================
    @api.response(200, 'API Success/Failure')
    def get(self):
        """
        API ping to check alive or not

        # Input
        ## Arguments
        None

        # JSON Output
        ## Attributes
        * success : bool : required : Success or Failure
        * http_method : str : not required : http method on request
        * message : str : not required : error message on failure

        ### Response Sample
        ``` json
        {
            "success": true,
            "http_method": "GET"
        }
        ```
        """
        r = None
        try:
            r = {'success': True, 'http_method': request.method}
        except Exception as exp:
            r = {'success': False, 'message': str(exp)}
        finally:
            return r

# Variable
# End-Point: http://{address}/api/variables/v1.0/var
# Parameters: path


variables_parser = reqparse.RequestParser()
variables_parser.add_argument('path', type=str, location=['form', 'args'])
variables_parser.add_argument('value', type=str, location='form')
###############################################################################
class Variables(Resource):
    @api.expect(variables_parser, validate=True)
    @api.response(200, 'API Success/Failure')
    @api.response(500, 'Internal Server Error')
    def get(self):
        args = variables_parser.parse_args()
        try:
            retv = variables.get_by_argos_variable(
                args['path'], raise_exception=True)
            return retv
        except ReferenceError as e:
            api.abort(404, str(e))

    # ==========================================================================
    @api.expect(variables_parser, validate=True)
    @api.response(200, 'API Success/Failure')
    @api.response(500, 'API Success/Failure')
    def post(self):
        json_data = request.get_json()
        value = variables.set_by_argos_variable(
            json_data['data']['path'], json_data['data']['value'])
        return value


###############################################################################
class Converter(Resource):
    @api.response(200, 'API Success/Failure')
    def post(self):
        json_data = request.get_json()
        value = variables.convert(json_data['data']['value'])
        return value


api.add_resource(Variables, '/variables')
api.add_resource(Converter, '/convert')
