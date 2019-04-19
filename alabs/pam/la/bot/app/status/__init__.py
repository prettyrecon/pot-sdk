import json
from flask import jsonify, send_file
from flask_restplus import Namespace, Resource, reqparse
from alabs.pam.la.bot import bot_th
from .parser import scenario_parser
from PIL import ImageGrab
import io

################################################################################
class ReturnValue(dict):
    def __init__(self, value):
        dict.__init__(self)
        self['data'] = value

    @property
    def json(self):
        print(self)
        return json.dumps(self, indent=4)

################################################################################
api = Namespace('status', description="Bot Rest API")


################################################################################
@api.route('/')
class BotScenario(Resource):
    def get(self):
        global bot_th
        data = bot_th.scenario
        # return ReturnValue(data).json
        return jsonify(ReturnValue(dict(data)))

    @api.expect(scenario_parser, validate=True)
    def post(self):
        """
        form-data 형식으로 시나리오 filename(path)를 받는다.
        :return:
        """
        global bot_th
        argspec = scenario_parser.parse_args()
        filename = argspec['filename']
        bot_th.scenario_filename = filename
        bot_th.load_scenario(filename)
        return jsonify(ReturnValue(dict(bot_th.scenario)))


################################################################################
class BotStart(Resource):
    @api.expect(scenario_parser, validate=True)
    @api.doc('bot_status')
    def post(self):
        global bot_th
        # json_data = request.get_json()
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
class PamRequestAvailableOperator(Resource):
    """
    현재 Platform 에서 사용 가능한 PAM 목록 제공
    """
    def get(self):
        # TODO: 현재는 더미 데이터를 반환.
        ret = {
            "data": [
                {"name": "SearchImage"},
                {"name": "MouseClick"},
                {"name": "MouseScroll"},
                {"name": "TypeText"},
                {"name": "Delay"},
                {"name": "Repeat"},
                {"name": "TypeKeys"},
                {"name": "EndScenario"},
                {"name": "EndStep"},
                {"name": "SetVariable"},
                {"name": "CompareText"},
                {"name": "DeleteFile"},
                {"name": "ExecuteProcess"},
                {"name": "StopProcess"},
                {"name": "StopProcess"},
            ]
        }
        return ret


################################################################################
class PamRequestScreenShot(Resource):
    """
    현재 화면을 캡쳐하여 반환
    """
    def get(self):
        # TODO: 플랫폼 판별은 환경변수를 사용하도록 변경해야 함
        img = ImageGrab.grab()
        buffer = io.BytesIO()
        img.save(buffer, 'PNG')
        buffer.seek(0)
        return send_file(
            buffer, attachment_filename='a.png', mimetype='image/png')


################################################################################
api.add_resource(PamRequestAvailableOperator, '/operators')
api.add_resource(PamRequestScreenShot, '/screenshot')

api.add_resource(BotScenario, '/scenario')
api.add_resource(BotStatus, '/scenario/status')
api.add_resource(BotStart, '/scenario/start')
api.add_resource(BotPause, '/scenario/pause')
api.add_resource(BotStop, '/scenario/stop')
api.add_resource(BotNext, '/scenario/next')
