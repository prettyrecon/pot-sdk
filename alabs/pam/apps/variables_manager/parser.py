
from flask_restx import reqparse

variables_parser = reqparse.RequestParser()
variables_parser.add_argument('path', type=str, location=['form', 'args'])
variables_parser.add_argument('value', type=str, location='form')
variables_parser.add_argument('name', type=str, location=['form', 'args'])
variables_parser.add_argument('format', type=str, location='form')
variables_parser.add_argument('debug', type=bool, location='args')


