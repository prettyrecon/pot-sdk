#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod:`alabs.pam.rap.autogui.dialogue
====================================
.. moduleauthor:: Deokyu Lim
.. note:: VIVANS License

Description
===========
ARGOS LABS PAM

Authors
===========

* Deokyu Lim

Change Log
--------

 * [2019/04/24]
    - starting
"""

################################################################################
import os
import platform
import enum
from alabs.common.definitions.platforms import Platforms

################################################################################
# Version
NUM_VERSION = (0, 9, 0)
VERSION = ".".join(str(nv) for nv in NUM_VERSION)
__version__ = VERSION

OWNER = 'ARGOS-LABS'
GROUP = 'Pam'
PLATFORM = ['darwin', 'linux']
OUTPUT_TYPE = 'json'
DESCRIPTION = 'Pam for HA. It reads json scenario files by LA Stu and runs'

class Action(enum.IntEnum):
    TITLE = 0
    NAME = 1
    PARAMS = 2

ACTION = {
    'Resume': 2,  # Resume scenario
    'MoveOn': 2,  # Go
    'TreatAsError': 2,
    'IgnoreFailure': 2,
    'AbortScenarioButNoError': 2,  # FinishScenario
    'JumpForward': 3,
    'JumpBackward': 3,
    'JumpToOperation': 3,
    'JumpToStep': 3,
    'RestartFromTop': 2
}


def check_args(argspec):
    global ACTION
    for arg in argspec.button:
        if arg[0] not in ACTION:
            raise ValueError("'{}' is not ButtonAction.".format(arg[0]))
        if len(arg) < ACTION[arg[0]]:
            raise ValueError("{} takes exactly {} arguments, ({} given)".format(
                arg[0], ACTION[arg[0]], len(arg)))
    return True


################################################################################
def main(*args):
    _platform = os.environ.get('ARGOS_RPA_PAM_PLATFORM', platform.system())
    if _platform == Platforms.LINUX.value:
        from alabs.pam.rpa.autogui.dialogue.linux import main as _main

    elif _platform == Platforms.WINDOWS.value:
        from alabs.pam.rpa.autogui.dialogue.linux import main as _main

    elif _platform == Platforms.MAC.value:
        from alabs.pam.rpa.autogui.dialogue.linux import main as _main

    elif _platform == Platforms.IOS.value:
        from alabs.pam.rpa.autogui.click.ios import main as _main
        # return _main('--wda_url', url, '--wda_port', port)
    else:
        raise Exception("{} is Not Supported Platform".format(_platform))
    return _main(*args)
