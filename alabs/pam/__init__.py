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
        from flask_restplus import Api

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
    parser = argparse.ArgumentParser()
    if not os.environ.setdefault('PAM_CONF', ''):
        path = pathlib.Path.home() / '.argos-rpa-pam.conf'
        os.environ['PAM_CONF'] = str(path)
    conf = get_conf()
    logger = get_logger(conf.get('/PATH/PAM_LOG'))

    parser.add_argument('-a', '--host', type=str,
                        default=conf.get('MANAGER/IP'), help='')
    parser.add_argument('-p', '--port', type=int,
                        default=conf.get('MANAGER/PORT'), help='')

    parser.add_argument('-f', '--filepath', type=str, default='',
                        help='JSON or BOT type of the scenario file')

    argspec = parser.parse_args()
    if not argspec.filepath:
        return pam_manager(argspec, logger)

    ############################################################################
    from alabs.pam.manager import PamManager as pm
    ext = pathlib.Path(argspec.filepath).suffix
    if 'bot' == ext[1:].lower():
        path = extract_bot_file(argspec.filepath, logger)
    elif 'json' == ext[1:].lower():
        path = argspec.filepath
    else:
        logger.error(
            '{} is not supported scenario format.'.format(argspec.filepath))
        print('{} is not supported scenario format.'.format(argspec.filepath))
        exit(-1)

    logger.info('Started Variable Manager.')
    p = Process(target=pam_manager, args=(argspec, logger))
    p.start()

    pam_mgr = pm()
    runner = pam_mgr.create(path)
    pam_mgr.start_runner(0)
    runner.RUNNER.join()
    p.kill()
    p.join()



