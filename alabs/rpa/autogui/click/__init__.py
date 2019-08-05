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

################################################################################
import os
import platform
import enum
from alabs.common.definitions.platforms import Platforms


################################################################################
class ClickMotionType(enum.Enum):
    CLICK = 'click'
    DOUBLE = 'doubleClick'
    PRESS = 'mouseDown'
    RELEASE = 'mouseUp'


################################################################################
class ClickType(enum.Enum):
    RIGHT = 'right'
    LEFT = 'left'
    NONE = 'None'

################################################################################
def to_int(value:str):
    return tuple((int(v) for v in value.split(',')))

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
def main(*args):
    _platform = os.environ.get('ARGOS_RPA_PAM_PLATFORM', platform.system())
    if _platform == Platforms.LINUX.value:
        from alabs.rpa.autogui.click.linux import main as _main

    elif _platform == Platforms.MAC.value:
        from alabs.rpa.autogui.click.linux import main as _main

    elif _platform == Platforms.IOS.value:
        from alabs.rpa.autogui.click.ios import main as _main
        # return _main('--wda_url', url, '--wda_port', port)
    else:
        raise Exception("{} is Not Supported Platform".format(_platform))
    return _main(*args)
