import json
from flask import request, jsonify
from flask_restplus import Namespace, Resource, reqparse
from alabs.pam.la.bot import bot_th


################################################################################
class ReturnValue(dict):
    def __init__(self, value):
        dict.__init__(self)
        self['data'] = value

    @property
    def json(self):
        return json.dumps(self)

################################################################################
api = Namespace('status', description="Bot Rest API")


################################################################################
scenario_parser = reqparse.RequestParser()
scenario_parser.add_argument('filename', type=str)
@api.route('/')
class BotScenario(Resource):
    def get(self):
        global bot_th
        data = bot_th.scenario
        return ReturnValue(data).json

    @api.expect(scenario_parser, validate=True)
    @api.doc('bot_status')
    def post(self):
        global bot_th
        json_data = request.get_json()
        filename = json_data['data']['filename']
        bot_th.scenario_filename = filename
        bot_th.load_scenario(filename)
        return jsonify(ReturnValue(dict(bot_th.scenario)))


################################################################################
class BotStart(Resource):
    @api.expect(scenario_parser, validate=True)
    @api.doc('bot_status')
    def post(self):
        global bot_th
        json_data = request.get_json()
        bot_th._debug_step_over = False
        bot_th._pause = False
        if not bot_th.isAlive():
            bot_th.start()
        return bot_th._pause

################################################################################
class BotPause(Resource):
    @api.doc('bot_status')
    def post(self):
        global bot_th
        bot_th._pause = True
        return True

################################################################################
class BotStop(Resource):
    def post(self):
        global bot_th
        bot_th.stop()
        return True


################################################################################
class BotNext(Resource):
    def post(self):
        global bot_th
        bot_th._debug_step_over = True
        bot_th._pause = False
        return True


################################################################################
class BotStatus(Resource):
    @api.expect(scenario_parser, validate=True)
    @api.doc('bot_status')
    def get(self):
        global bot_th
        data = dict()
        data['is_running'] = bot_th.is_running
        data['current_item'] = bot_th.scenario.item
        return data


################################################################################
api.add_resource(BotScenario, '/scenario')
api.add_resource(BotStatus, '/scenario/status')
api.add_resource(BotStart, '/scenario/start')
api.add_resource(BotPause, '/scenario/pause')
api.add_resource(BotStop, '/scenario/stop')
api.add_resource(BotNext, '/scenario/next')
