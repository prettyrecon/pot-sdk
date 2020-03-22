#!/usr/bin/env python
import json
from flask_rextx import Namespace, Resource
from flask import request, jsonify, make_response
from alabs.pam.variable_manager import variables, number_format
from alabs.pam.apps.variables_manager.parser import variables_parser

api = Namespace('variables', description='Variables Manager API')
VAR_API_PREFIX = 'api'
VAR_API_VERSION = 'v1.0'
VAR_API_NAME = 'var'

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

###############################################################################
@api.route('/variables')
class Variables(Resource):
    @api.expect(variables_parser, validate=True)
    @api.response(200, 'API Success/Failure')
    @api.response(500, 'Internal Server Error')
    def get(self):
        args = variables_parser.parse_args()
        try:
            if args['debug']:
                return variables
            retv = variables.get_by_argos_variable(
                args['path'], args['name'], raise_exception=True)
            return retv
        except ReferenceError as e:
            # 찾고자 하는 데이터 없음
            api.abort(make_response(jsonify(message=str(e)), 207))
        except ValueError as e:
            api.abort(make_response(jsonify(message=str(e)), 400))
        except Exception as e:
            api.abort(500, str(e))

    # ==========================================================================
    @api.expect(variables_parser, validate=True)
    @api.response(200, 'API Success/Failure')
    @api.response(500, 'API Success/Failure')
    def post(self):
        try:
            json_data = request.get_json()
            value = variables.set_by_argos_variable(
                json_data['data']['path'], json_data['data']['value'],
                json_data['data']['name'])
            return value
        except json.decoder.JSONDecodeError as e:
            message = 'Failed to load json data: {}'
            api.abort(api.abort(
                make_response(jsonify(message=message.format(str(e))), 400)))
        except ValueError as e:
            api.abort(make_response(jsonify(message=str(e)), 400))
        except Exception as e:
            api.abort(500, message=e)


###############################################################################
@api.route('/convert')
class Converter(Resource):
    @api.response(200, 'API Success/Failure')
    def post(self):
        json_data = request.get_json()
        try:
            value = variables.convert(
                json_data['data']['value'],
                json_data['data']['name'])
            return value
        except ReferenceError as e:
            # 찾고자 하는 데이터 없음
            api.abort(make_response(jsonify(message=str(e)), 207))
        except ValueError as e:
            api.abort(make_response(jsonify(message=str(e)), 400))
        except Exception as e:
            api.abort(500, str(e))


###############################################################################
@api.route('/calculate')
class Calculate(Resource):
    @api.expect(variables_parser)
    def post(self):
        try:
            json_data = request.get_json()
            ret = variables.calculate(
                json_data['data']['value'],
                json_data['data']['name'])
            if 'format' in json_data['data']:
                ret = number_format(ret, json_data['data']['format'])
            return ret
        except ReferenceError as e:
            # 찾고자 하는 데이터 없음
            api.abort(make_response(jsonify(message=str(e)), 207))
        except ValueError as e:
            api.abort(make_response(jsonify(message=str(e)), 400))
        except Exception as e:
            api.abort(500, str(e))
