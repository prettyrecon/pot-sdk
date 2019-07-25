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

import sys
import pdb

from gevent import monkey
monkey.patch_all()
from gevent.pywsgi import WSGIServer

from flask import Flask
from flask_restplus import Api

from alabs.common.util.vvargs import ModuleContext
from alabs.pam.apps.pam_manager.app import api as ns_manager

from alabs.pam.apps.bot_store_handler.app import api as bot_store_api
from alabs.pam.apps.bot_store_handler import BOT_API_NAME 
from alabs.pam.apps.bot_store_handler import BOT_API_PREFIX 
from alabs.pam.apps.bot_store_handler import BOT_API_VERSION 

from alabs.pam.apps.variables_manager.app import api as variables_mgr_api
from alabs.pam.apps.variables_manager.app import VAR_API_NAME
from alabs.pam.apps.variables_manager.app import VAR_API_PREFIX
from alabs.pam.apps.variables_manager.app import VAR_API_VERSION

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
def pam_manager(mcxt, argspec):
    try:
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

        mcxt.logger.info("Start PAM-Manager from [%s]..." % __name__)
        mcxt.logger.info("Start BOT-Handler from [%s]..." % __name__)
        mcxt.logger.info("Start VAR-Manager from [%s]..." % __name__)

        api.init_app(app)
    except Exception as err:
        if mcxt.logger:
            mcxt.logger.error('Error: %s' % str(err))
        raise

    http = WSGIServer((argspec.host, argspec.port), app.wsgi_app)
    http.serve_forever()



################################################################################
def _main(*args):
    """
    Build user argument and options and call plugin job function
    :param args: user arguments
    :return: return value from plugin job function

    ..note:: _main 함수에서 사용되는 패러미터(옵션) 정의 방법
플러그인 모듈은 ModuleContext 을 생성하여 mcxt를 with 문과 함께 사용
    owner='ARGOS-LABS',
    group='pam',
    version='1.0',
    platform=['darwin'],
    output_type='text',
    description='HA Bot for LA',
    test_class=TU,
    """
    with ModuleContext(
        owner=OWNER,
        group=GROUP,
        version=VERSION,
        platform=PLATFORM,
        output_type=OUTPUT_TYPE,
        description=DESCRIPTION,
    ) as mcxt:
        mcxt.add_argument('-a', '--host', type=str, default='127.0.0.1',
                          help='')
        mcxt.add_argument('-p', '--port', type=int, default=8012, help='')

        argspec = mcxt.parse_args(args)
        return pam_manager(mcxt, argspec)


################################################################################
def main(*args):
    return _main(*args)
