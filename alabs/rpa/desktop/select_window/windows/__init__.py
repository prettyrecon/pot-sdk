#!/usr/bin/env python
"""
====================================
 :mod:`alabs.pam.la.bot2py
====================================
.. moduleauthor:: Raven Lim <deokyu@argos-labs.com>
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
import os
from alabs.common.util.vvargs import ModuleContext, func_log, str2bool, \
    ArgsError, ArgsExit
from pathlib import Path

################################################################################
# Version
NUM_VERSION = (0, 9, 0)
VERSION = ".".join(str(nv) for nv in NUM_VERSION)
__version__ = VERSION

OWNER = 'ARGOS-LABS'
GROUP = 'Pam'
PLATFORM = ['windows',]
OUTPUT_TYPE = 'json'
DESCRIPTION = 'Selecting Window'


################################################################################
@func_log
def select_window(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: actual delay seconds
    """
    mcxt.logger.info('>>>starting...')
    print(argspec)
    mcxt.logger.info('>>>end...')
    return

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
        # select_window 'Untitled' 'Notepad.exe'
        # select_window 'Untitled' 'Notepad.exe' -l 10 20
        # select_window 'Untitled' 'Notepad.exe' -s 100 200
        # select_window 'Untitled' 'Notepad.exe' -c 110 210

        mcxt.add_argument('title', type=str, help='App Title')
        mcxt.add_argument('name', type=str, help='App Name')
        mcxt.add_argument('-l', '--location', nargs=2, type=int,
                          help='Set Location')
        mcxt.add_argument('-s', '--size', nargs=2, type=int,
                          help='Set Size')
        mcxt.add_argument('-c', '--click', nargs=2, type=int,
                          help='Click Point')
        argspec = mcxt.parse_args(args)
        return select_window(mcxt, argspec)

################################################################################
def main(*args):
    return _main(*args)