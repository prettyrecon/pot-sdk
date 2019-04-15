from flask_restplus import reqparse

scenario_parser = reqparse.RequestParser()
scenario_parser.add_argument('filename', type=str, location='form',
                             help="scenario filename")
