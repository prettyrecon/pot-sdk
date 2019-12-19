#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod:`alabs.pam.la.bot2py
====================================
.. moduleauthor:: Duk Kyu Lim <deokyu@argos-labs.com>
.. note:: ARGOS-LABS License

Description
===========
ARGOS LABS PAM For LA

Authors
===========

* Raven Lim

Change Log
--------

 * [2019/01/30]
    - starting
"""

################################################################################
import sys

from subprocess import Popen, PIPE

from alabs.common.util.vvargs import ModuleContext
from alabs.common.util.vvlogger import StructureLogFormat


################################################################################
# Version
NUM_VERSION = (0, 9, 0)
VERSION = ".".join(str(nv) for nv in NUM_VERSION)
__version__ = VERSION

OWNER = 'ARGOS-LABS'
GROUP = 'Pam'
PLATFORM = ['windows', 'darwin', 'linux']
OUTPUT_TYPE = 'json'
DESCRIPTION = 'Pam for HA. It reads json scenario files by LA Stu and runs'

import os

################################################################################
def execute_process(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: True
    """
    mcxt.logger.info('ExecuteProcess is Running...')
    mcxt.logger.debug(StructureLogFormat(ARGS_SPEC=argspec.__dict__))

    proc = Popen('{}'.format(argspec.command), shell=True, stdout=PIPE)
    ret = {'PID': proc.pid, 'PROC': proc, 'NAME': argspec.command.split()[0]}
    mcxt.logger.info('TypeText is Done')
    return ret[argspec.ret]


################################################################################
def _main(*args):
    with ModuleContext(
        owner=OWNER,
        group=GROUP,
        version=VERSION,
        platform=PLATFORM,
        output_type=OUTPUT_TYPE,
        description=DESCRIPTION,
    ) as mcxt:
        mcxt.add_argument('command', help='Command to execute')
        mcxt.add_argument('--ret', choices=['PROC', 'PID', 'NAME'], type=str,
                          default='PID',
                          help='Command to execute')

        argspec = mcxt.parse_args(args)
        return execute_process(mcxt, argspec)

################################################################################
def main(*args):
    return _main(*args)

