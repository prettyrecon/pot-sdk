
from flask_restplus import Namespace, Resource, fields

api = Namespace('status', description="Bot Rest API")

@api.route('/')
class Status(Resource):
    @api.doc('bot_status')
    def get(self):
        return "Hello World"


