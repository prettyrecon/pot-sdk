import werkzeug
from flask_restplus import reqparse
from flask_restplus import reqparse

file_upload = reqparse.RequestParser()
file_upload.add_argument(
    'zip_file', type=werkzeug.datastructures.FileStorage, location='files',
    required=True, help='ZIP file')

bot_parser = reqparse.RequestParser()
bot_parser.add_argument('index', type=int, action='append', location='args')
