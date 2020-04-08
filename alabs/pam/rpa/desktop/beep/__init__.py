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



################################################################################
def main(*args):
    _platform = os.environ.get('ARGOS_RPA_PAM_PLATFORM', platform.system())
    # if _platform == 'Linux':
    #     from alabs.pam.rpa.desktop.compare_text.linux import main as _main

    if _platform == 'Windows':
        from alabs.pam.rpa.desktop.beep.windows import main as _main

    # elif _platform == 'Darwin':
    #     from alabs.pam.rpa.desktop.compare_text.linux import main as _main

    # elif _platform == 'iOS':
    #     from alabs.pam.rpa.autogui.click.ios import main as _main
        # return _main('--wda_url', url, '--wda_port', port)
    else:
        raise Exception("{} is Not Supported Platform".format(_platform))
    return _main(*args)
