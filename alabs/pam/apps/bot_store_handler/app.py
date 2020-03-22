
import pathlib
import tempfile
import traceback
from flask import jsonify, make_response
from flask import request
from werkzeug.exceptions import BadRequest

from flask_rextx import Namespace, Resource

from alabs.pam.apps.bot_store_handler.parser import file_upload
from alabs.pam.scenario_repository import ScenarioRepoHandler
from alabs.common.util.vvhash import get_file_md5
from .parser import bot_parser

api = Namespace('bots', description="Bot Rest API")


################################################################################
@api.route('')
class BotHandler(Resource):
    # ==========================================================================
    def get(self):
        bh = ScenarioRepoHandler()
        return bh.get_bots_with_zip_file()

    # ==========================================================================
    @api.expect(file_upload)
    def post(self):
        """
        전송 받은 BOT 파일을 STORE에 저장
        """
        try:
            # 파일요청 처리
            file = request.files['file']
            # TODO: 윈도우 환경은 고려되어 있지 않음
            filename = request.form['fileName']
            tempdir = tempfile.gettempdir()
            filepath = str(pathlib.Path(tempdir, filename))
            file.save(filepath)

            # HASH 검사
            source_hash = request.form['md5'].lower()
            target_hash = get_file_md5(filepath)
            if source_hash != target_hash:
                raise ValueError("The hashes are not equal. {} != {}".format(
                    source_hash, target_hash))

            bh = ScenarioRepoHandler()
            bh.add_bot_with_zip_file(filepath)
        except ValueError as e:
            api.abort(api.abort(make_response(jsonify(message=str(e)), 207)))
        except Exception as e:
            print(e)
            api.abort(400)

    # ==========================================================================
    @api.expect(bot_parser, validate=True)
    def delete(self):
        try:
            args = bot_parser.parse_args()
            if not args['index']:
                raise IndexError("The index parameter is required.")

            bh = ScenarioRepoHandler()
            bh.remove_bots_zip_file(args['index'])
        except IndexError as e:
            message = 'Failed to delete the scenario: {}'
            api.abort(api.abort(
                make_response(jsonify(message=message.format(str(e))), 207)))
        except Exception as e:
            traceback.print_exc()
            print(e)
            api.abort(400)
