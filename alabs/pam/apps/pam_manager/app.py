import os
import pathlib
import zipfile
import tempfile
from flask_restplus import Namespace, Resource
from flask import request, send_file
api = Namespace('manager', description="PAM MANAGER")
# from alabs.pam.scenario import Scenario
import traceback

from flask import jsonify, make_response
from alabs.pam.manager import PamManager as pm
from alabs.pam.scenario_repository import ScenarioRepoHandler
from alabs.pam.apps.pam_manager.parser import pam_parser, file_upload
from alabs.common.util.vvhash import get_file_md5
from alabs.pam.rpa.desktop.screenshot import main as screenshot
from alabs.common.util.vvlogger import get_logger, StructureLogFormat
from alabs.pam.conf import get_conf

logger = get_logger(get_conf().get('/PATH/PAM_LOG'))

from alabs.pam.runner import is_timeout


BOTS = list()
PAM_MANAGER = pm()

#
# GET /api/v1.0/pam
# POST /api/v1.0/pam  args: scenario_number
# DELETE /api/v1.0/pam args: pam number

# POST /api/v1.0/pam/start/0


def get_pam_info(pam:PAM_MANAGER.RunnerInfo):
    key = ['name', 'bot_name', 'bot_description',
           'is_running', 'venv_path', 'status']
    value = [pam.RUNNER.name,
             pam.RUNNER.scenario.name,
             pam.RUNNER.scenario.description,
             pam.RUNNER.is_alive(),
             pam.RUNNER.venv_path,]
    if pam.PIPE.poll():
        value.append(pam.PIPE.recv())
    data = dict(zip(key, value))
    return data

################################################################################
@api.route('')
class PamManager(Resource):
    # PAM 목록보기 ##############################################################
    def get(self):
        """
        @startuml
        title
            PAM 생성 및 운영
        end title

        actor USER
        participant PamManager

        USER -> PamManager: GET 현재 PAM 목록 요청
        activate PamManager
        return PAM 목록 반환
        @enduml
        :return:
        """
        global PAM_MANAGER
        result = list()
        for pam in PAM_MANAGER:
            result.append(get_pam_info(pam))
        return result

    # PAM 생성 #################################################################
    @api.expect(file_upload, validate=True)
    def post(self):
        """
        @startuml
        actor USER
        USER -> Pam: Runner 생성 요청
        activate Pam
        Pam -> Pam: Runner 생성
        Pam -> Pam: Runner 목록에 추가
        return Boolean
        @enduml
        :return:
        """
        # TODO: 현재는 BOT을 가지지 않은 RUNNER는 생성되지 못하게 한다.
        global PAM_MANAGER

        try:
            # PAM 초기화
            for runner in PAM_MANAGER:
                del runner

            # 파일 받기 ---------------------------------------------------------
            file = request.files['file']
            filename = request.form['fileName']
            tempdir = tempfile.gettempdir()
            filepath = str(pathlib.Path(tempdir, filename))
            file.save(filepath)
            logger.info('Received the scenario file.')
            logger.debug(StructureLogFormat(FILE_PATH=filepath))

            # HASH 검사
            source_hash = request.form['md5'].lower()
            target_hash = get_file_md5(filepath)
            # if source_hash != target_hash:
            #     raise ValueError("The hashes are not equal. {} != {}".format(
            #         source_hash, target_hash))

            # tempdir 생성
            tempdir = pathlib.Path(tempfile.gettempdir()) / \
                      pathlib.Path(ScenarioRepoHandler.STORE_DIR)
            # 압축해제할 위치명 생성
            name = pathlib.Path(filepath).name
            name = name.split('.')[0]
            path = str(pathlib.Path(tempdir, '', name))
            # 압축해제 후 Runner 생성
            with zipfile.ZipFile(filepath) as file:
                file.extractall(path)
            # path = pathlib.Path(path, name + '.json')
            path = pathlib.Path(path, 'Scenario.json')
            PAM_MANAGER.create(path)
            return True

        except IndexError as e:
            message = 'Failed to make a PAM with scenario: {}'
            api.abort(api.abort(
                make_response(jsonify(message=message.format(str(e))), 207)))
        except Exception as e:
            traceback.print_exc()
            print(e)
            api.abort(500)
            pass

    # PAM 생성 #################################################################
    @api.expect(pam_parser, validate=True)
    def delete(self):
        global PAM_MANAGER
        try:
            args = pam_parser.parse_args()
            if not args['index']:
                raise ValueError("Bot Index Needed!")
            PAM_MANAGER.stop_runners(args['index'])
            PAM_MANAGER.remove_runners(args['index'])
        except IndexError as e:
            message = 'Failed to delete the PAM: {}'
            api.abort(api.abort(
                make_response(jsonify(message=message.format(str(e))), 207)))
        except Exception as e:
            traceback.print_exc()
            api.abort(500)

################################################################################
@api.route('/<int:index>')
@api.param('index')
class Pam(Resource):
    def get(self, index):
        global PAM_MANAGER
        try:
            pam = PAM_MANAGER[index]
            return get_pam_info(pam)
        except Exception as e:
            traceback.print_exc()
            api.abort(500)

    def delete(self, index):
        global PAM_MANAGER

################################################################################
@api.route('/<int:index>/start')
@api.param('index')
class PamActions(Resource):
    def post(self, index):
        global PAM_MANAGER
        try:
            PAM_MANAGER.start_runner(index)
        except IndexError as e:
            message = 'Failed to start the pam: {}'
            api.abort(api.abort(
                make_response(jsonify(message=message.format(str(e))), 207)))
        except Exception as e:
            traceback.print_exc()
            print(e)
            api.abort(400)

################################################################################
@api.route('/<int:index>/stop')
@api.param('index')
class PamActions(Resource):
    def post(self, index):
        global PAM_MANAGER
        pass

################################################################################
@api.route('/<int:index>/pause')
@api.param('index')
class PamActions(Resource):
    def post(self, index):
        global PAM_MANAGER
        pass


################################################################################
@api.route('/screenshot')
class PamScreenShot(Resource):
    def get(self):
        buffer = screenshot()
        return send_file(
            buffer, attachment_filename='a.png', mimetype='image/png')

# ################################################################################
# @api.route('/<int:uid>/start')
# class BotStart(Resource):
#     def post(self, uid):
#         global bot_th
#         # json_data = request.get_json()
#         PAM_MANAGER.start_runner(-1)
#         runner = PAM_MANAGER.get_runner(0)
#         runner.RUNNER._debug_step_over = False
#         runner.RUNNER._pause = False
#         runner.PIPE.send(('play',))
#         # if not bot_th.isAlive():
#         #     bot_th.start()
#         return