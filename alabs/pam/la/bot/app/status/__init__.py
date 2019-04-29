import json
import zipfile
import pathlib
import time
from flask import jsonify, send_file
from flask_restplus import Namespace, Resource, reqparse
from alabs.pam.la.bot import bot_th
from .parser import scenario_parser
from alabs.common.util.vvhash import get_file_md5

from alabs.rpa.desktop.screenshot import main

################################################################################
class ReturnValue(dict):
    def __init__(self, value):
        dict.__init__(self)
        self['data'] = value

    @property
    def json(self):
        return json.dumps(self, indent=4)

################################################################################

api = Namespace('status', description="Bot Rest API")

import werkzeug
from flask import request

file_upload = reqparse.RequestParser()
file_upload.add_argument('zip_file',
                         type=werkzeug.datastructures.FileStorage,
                         location='files',
                         required=True,
                         help='ZIP file')


################################################################################
class BotScenario(Resource):
    def get(self):
        global bot_th
        data = bot_th.scenario
        # return ReturnValue(data).json
        return jsonify(ReturnValue(dict(data)))

    @api.expect(file_upload)
    def post(self):
        try:
            file = request.files['file']
            # TODO: 윈도우 환경은 고려되어 있지 않음
            filepath = '%s%s' % ('/tmp/', 'scenario.zip')
            file.save(filepath)
            scn_zip = zipfile.ZipFile(filepath)
            # TODO: 설정으로 PATH를 설정할 수 있어야 함
            extpath = str(pathlib.Path.home()) + \
                      str(pathlib.PurePath('/Scenarios'))
            scn_zip.extractall(extpath)
            scn_zip.close()

            filename = extpath + \
                       str(pathlib.PurePath('/' + request.form['fileName']))

            # HASH 검사
            source_hash = request.form['md5'].lower()
            target_hash = get_file_md5(filepath)
            # if source_hash != target_hash:
            #     raise Exception("The hash are not equal")

            # 설정
            bot_th.scenario_filename = filename
            bot_th.command_q.put(('_load_scenario', filename))
            time.sleep(1)
        except Exception as e:
            print(e)
            api.abort(400)

        # return jsonify(ReturnValue(dict(bot_th.scenario)))



################################################################################
class BotStart(Resource):
    @api.expect(scenario_parser, validate=True)
    @api.doc('bot_status')
    def post(self, scn_number):
        global bot_th
        # json_data = request.get_json()
        bot_th._debug_step_over = False
        bot_th._pause = False
        # if not bot_th.isAlive():
        #     bot_th.start()
        return bot_th._pause

################################################################################
class BotPause(Resource):
    @api.doc('bot_status')
    def post(self, scn_number):
        global bot_th
        bot_th._pause = True
        return True

################################################################################
class BotStop(Resource):
    def post(self, scn_number):
        global bot_th
        bot_th.command_q.put(('stop',))
        return True


################################################################################
class BotNext(Resource):
    def post(self, scn_number):
        global bot_th
        bot_th._debug_step_over = True
        bot_th._pause = False
        return True


################################################################################
class BotStatus(Resource):
    @api.expect(scenario_parser, validate=True)
    @api.doc('bot_status')
    def post(self, scn_number):
        global bot_th
        print(repr(bot_th.status_message))
        return bot_th.status_message


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
                {"name": "ImageMatch"},
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
        buffer = main()
        return send_file(
            buffer, attachment_filename='a.png', mimetype='image/png')


################################################################################
api.add_resource(PamRequestAvailableOperator, '/operators')
api.add_resource(PamRequestScreenShot, '/screenshot')

api.add_resource(BotScenario, '/scenario')
# api.add_resource(BotScenario, '/scenario/<int:scn_number>/')
api.add_resource(BotStatus, '/scenario/<int:scn_number>/status')
api.add_resource(BotStart, '/scenario/<int:scn_number>/run')
api.add_resource(BotPause, '/scenario/<int:scn_number>/pause')
api.add_resource(BotStop, '/scenario/<int:scn_number>/stop')
api.add_resource(BotNext, '/scenario/<int:scn_number>/next')
