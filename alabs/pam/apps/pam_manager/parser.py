import werkzeug
from flask import request
from flask_restplus import reqparse

file_upload = reqparse.RequestParser()
file_upload.add_argument('zip_file',
                         type=werkzeug.datastructures.FileStorage,
                         location='files',
                         required=True,
                         help='ZIP file')

pam_parser = reqparse.RequestParser()
pam_parser.add_argument('index', type=int, action='append', location='args')
pam_parser.add_argument('bot_index', type=int, location='args')
