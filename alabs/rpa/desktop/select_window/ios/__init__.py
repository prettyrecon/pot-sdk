#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod:`alabs.rpa.desktop.execute_process
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

 * [2019/04/22]
    - starting
"""

################################################################################
import wda
from alabs.common.util.vvargs import ModuleContext, func_log, str2bool, \
    ArgsError, ArgsExit

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

################################################################################
class client_alabs(wda.Client):
    def session(self, bundle_id=None, arguments=None, environment=None):
        if bundle_id is None:
            sid = self.status()['sessionId']
            if not sid:
                raise RuntimeError("no session created ever")
            http = self.http.new_client('session/'+sid)
            return session_alabs(http, sid)

        if arguments and type(arguments) is not list:
            raise TypeError('arguments must be a list')

        if environment and type(environment) is not dict:
            raise TypeError('environment must be a dict')

        capabilities = {
            'bundleId': bundle_id,
            'arguments': arguments,
            'environment': environment,
            'shouldWaitForQuiescence': True,
        }
        # Remove empty value to prevent WDAError
        for k in list(capabilities.keys()):
            if capabilities[k] is None:
                capabilities.pop(k)

        data = wda.json.dumps({
            'desiredCapabilities': capabilities
        })
        res = self.http.post('session', data)
        httpclient = self.http.new_client('session/'+res.sessionId)
        return session_alabs(httpclient, res.sessionId)

################################################################################
class session_alabs(wda.Session):
    def activate(self, bundle_id):
        return self.http.post('/wda/apps/activate', dict(bundleId=bundle_id))

################################################################################
@func_log
def select_window(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: True
    """
    mcxt.logger.info('>>>starting...')
    client = client_alabs(url='{url}:{port}'.format(url=argspec.wda_url,
                                                 port=argspec.wda_port))
    if argspec.activate is None:
        session = client.session(bundle_id=argspec.bundle_id,
                                 arguments=argspec.args)
    else:
        session = client.session()
        session.activate(bundle_id=argspec.bundle_id)
    mcxt.logger.info(session.bundle_id)
    mcxt.logger.info('>>>end...')
    return session.bundle_id


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
    platform=['windows', 'darwin', 'linux'],
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
        ###################################### for app dependent parameters
        mcxt.add_argument('bundle_id', help='Application bundle id')
        mcxt.add_argument('--args', type=str, nargs='+',
                          help='-u https://www.google.com/ncr', default=None)
        mcxt.add_argument('--activate', type=bool,
                          help='True or False')
        mcxt.add_argument('--wda_url', type=str,
                          default='http://localhost', help='')
        mcxt.add_argument('--wda_port', type=str, default='8100', help='')

        argspec = mcxt.parse_args(args)
        return select_window(mcxt, argspec)

################################################################################
def main(*args):
    return _main(*args)