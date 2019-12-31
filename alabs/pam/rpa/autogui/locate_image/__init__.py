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
    if _platform == 'Linux':
        from alabs.pam.rpa.autogui.locate_image.linux import main as _main
    elif _platform == 'Windows':
        from alabs.pam.rpa.autogui.locate_image.linux import main as _main
    elif _platform == 'Darwin':
        from alabs.pam.rpa.autogui.locate_image.macos import main as _main

    elif _platform == Platforms.IOS.value:
        from alabs.pam.rpa.autogui.locate_image.ios import main as _main

    else:
        raise Exception("{} is Not Supported Platform".format(_platform))
    return _main(*args)
