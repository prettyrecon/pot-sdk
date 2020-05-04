#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod:`alabs.pam.la.bot2py
====================================
.. moduleauthor:: Injoong Kim <nebori92@argos-labs.com>
.. note:: VIVANS License

Description
===========
ARGOS LABS PAM For LA

Authors
===========

* Injoong Kim

Change Log
--------

 * [2019/04/24]
    - starting
"""
import os
import sys
import pdb
import pathlib
import argparse
import zipfile
import tempfile
from multiprocessing import Process

from alabs.common.util.vvargs import ModuleContext, func_log, \
    ArgsError, ArgsExit, get_icon_path
from alabs.common.util.vvlogger import StructureLogFormat, get_logger
from alabs.pam.conf import get_conf

################################################################################
# Version
NUM_VERSION = (0, 9, 0)
VERSION = ".".join(str(nv) for nv in NUM_VERSION)
__version__ = VERSION

OWNER = 'ARGOS-LABS'
GROUP = 'Pam'
PLATFORM = ['darwin']
OUTPUT_TYPE = 'json'
DESCRIPTION = 'Pam for HA. It reads json scenario files by LA Stu and runs'

PAM_API_PREFIX = 'api'
PAM_API_VERSION = 'v1.0'
PAM_API_NAME = 'pam'


################################################################################
class ForkedPdb(pdb.Pdb):
    """
    멀티프로세싱 사용시 자식 프로세스 디버깅에 사용
    ForkedPdb.set_trace() 를 pdb 호출 하고자 하는 위치에 삽입
    """
    def interaction(self, *args, **kwargs):
        _stdin = sys.stdin
        try:
            sys.stdin = open('/dev/stdin')
            pdb.Pdb.interaction(self, *args, **kwargs)
        finally:
            sys.stdin = _stdin


################################################################################
def pam_manager(argspec, logger):
    try:
        from gevent import monkey
        monkey.patch_all()
        from gevent.pywsgi import WSGIServer
        from flask import Flask
        from flask_restx import Api

        from alabs.pam.apps.pam_manager.app import api as ns_manager

        from alabs.pam.apps.bot_store_handler.app import api as bot_store_api
        from alabs.pam.apps.bot_store_handler import BOT_API_NAME
        from alabs.pam.apps.bot_store_handler import BOT_API_PREFIX
        from alabs.pam.apps.bot_store_handler import BOT_API_VERSION

        from alabs.pam.apps.variables_manager.app import \
            api as variables_mgr_api
        from alabs.pam.apps.variables_manager.app import VAR_API_NAME
        from alabs.pam.apps.variables_manager.app import VAR_API_PREFIX
        from alabs.pam.apps.variables_manager.app import VAR_API_VERSION

        # Flask app
        app = Flask(__name__)
        api = Api(title='ARGOS PAM-Manager', version='1.0',
                  description='PAM Manager')

        end_point = "/{PREFIX}/{VERSION}/{NAME}"
        api.add_namespace(ns_manager, path=end_point.format(
            PREFIX=PAM_API_PREFIX,
            VERSION=PAM_API_VERSION,
            NAME=PAM_API_NAME))

        api.add_namespace(bot_store_api, path=end_point.format(
            PREFIX=BOT_API_PREFIX,
            VERSION=BOT_API_VERSION,
            NAME=BOT_API_NAME))

        api.add_namespace(variables_mgr_api, path=end_point.format(
            PREFIX=VAR_API_PREFIX,
            VERSION=VAR_API_VERSION,
            NAME=VAR_API_NAME))

        api.init_app(app)
        logger.info('Starting PAM Manager...')

        http = WSGIServer((argspec.host, argspec.port), app.wsgi_app)
        http.serve_forever()
    except Exception as err:
        logger.error(str(err))
        raise

def extract_bot_file(filepath, logger):
    from alabs.pam.scenario_repository import ScenarioRepoHandler
    # tempdir 생성
    tempdir = pathlib.Path(tempfile.gettempdir()) / \
              pathlib.Path(ScenarioRepoHandler.STORE_DIR)
    # 압축해제할 위치명 생성
    name = pathlib.Path(filepath).name
    name = name.split('.')[0]
    path = str(pathlib.Path(tempdir, '', name))
    # 압축해제 후 Runner 생성
    logger.info('Extracting the bot file...')
    logger.debug(StructureLogFormat(BOT_FILE=filepath,
                                    TARGET_PATH=path))
    with zipfile.ZipFile(filepath) as file:
        file.extractall(path)
    path = pathlib.Path(path, 'Scenario.json')
    return path

################################################################################
def _main(*args):
    # 설정 파일

    if not os.environ.setdefault('PAM_CONF', ''):
        path = pathlib.Path.home() / '.argos-rpa-pam.conf'
        os.environ['PAM_CONF'] = str(path)
    configure = get_conf()

    # logger = get_logger(configure.get('/PATH/PAM_LOG'))
    # logger.info("="*80)

    log_path = configure.get('/PATH/PAM_LOG')
    # logger.info("="*80)

    with ModuleContext(
            owner='ARGOS-LABS',
            group='ai',
            version='1.0',
            platform=['windows', 'darwin', 'linux'],
            output_type='text',
            display_name='Text to Speech',
            icon_path=get_icon_path(__file__),
            description='Text to Speech using AI engine (google, ...)',
    ) as mcxt:

        mcxt.add_argument('-a', '--host', type=str,
                            default=configure.get('MANAGER/IP'), help='')
        mcxt.add_argument('-p', '--port', type=int,
                            default=configure.get('MANAGER/PORT'), help='')

        mcxt.add_argument('-f', '--filepath', type=str, default='',
                           help='JSON or BOT type of the scenario file')


        args = list(sys.argv[1:])
        args += ['--logfile', log_path]
        argspec = mcxt.parse_args(args)

        mcxt.logger.info("Arguments Parsing...")
        mcxt.logger.debug(StructureLogFormat(ARGUMENTS=str(argspec)))
        if not argspec.filepath:
            return pam_manager(argspec, mcxt.logger)

    ############################################################################
        from alabs.pam.manager import PamManager as pm
        ext = pathlib.Path(argspec.filepath).suffix
        if 'bot' == ext[1:].lower():
            path = extract_bot_file(argspec.filepath, mcxt.logger)
        elif 'json' == ext[1:].lower():
            path = argspec.filepath
        else:
            mcxt.logger.error(
                '{} is not supported scenario format.'.format(argspec.filepath))
            print('{} is not supported scenario format.'.format(argspec.filepath))
            exit(-1)
        mcxt.logger.info('Started Variable Manager.')
        p = Process(target=pam_manager, args=(argspec, mcxt.logger))
        p.start()

        pam_mgr = pm()
        runner = pam_mgr.create(path)
        try:
            pam_mgr.start_runner(0)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(e)
        runner.RUNNER.join()
        mcxt.logger.info('A process is joined gracefully.')
        mcxt.logger.info('Trying to destroy the variable manager...')
        p.kill()
        p.join()
        mcxt.logger.info('Variable Manager is joined gracefully')
        mcxt.logger.info('Finished.')




