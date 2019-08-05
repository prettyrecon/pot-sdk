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
def select_window_for_windows(mcxt, argspec):
    """

    :param mcxt:
    :param argspec:
    :return:
    """


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
    files = [Path(f) for f in argspec.files]
    result = list()
    for file in files:
        if not file.exists():
            result.append((str(file), "file not found"))
            continue
        try:
            os.remove(str(file))
        except OSError as e:
            result.append((str(file), e.strerror))
    mcxt.logger.info('>>>end...')
    return result

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
        mcxt.add_argument('files', type=str, nargs='+', help='Files')
        argspec = mcxt.parse_args(args)
        return select_window(mcxt, argspec)

################################################################################
def main(*args):
    return _main(*args)

