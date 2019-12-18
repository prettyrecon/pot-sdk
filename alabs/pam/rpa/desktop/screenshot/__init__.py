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
import tempfile
import pathlib
import json

from alabs.common.definitions.platforms import Platforms


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
        from alabs.pam.rpa.desktop.screenshot.linux import main as _main
        args = ['--path', '/tmp/tmp.png']
    elif _platform == Platforms.MAC.value:
        from alabs.pam.rpa.desktop.screenshot.macos import main as _main
        args = ['--path', '/tmp/tmp.png']
    elif _platform == Platforms.WINDOWS.value:
        from alabs.pam.rpa.desktop.screenshot.linux import main as _main
        tempdir = pathlib.Path(tempfile.gettempdir())
        temppng = tempdir / pathlib.Path('temp.png')
        args = ['--path', str(temppng)]
    elif _platform == Platforms.IOS.value:
        from alabs.pam.rpa.desktop.screenshot.ios import main as _main
        url = os.environ.get("ARGOS_RPA_WDA_URL", "http://localhost")
        port = os.environ.get("ARGOS_RPA_WDA_PORT", "8100")
        return _main('--wda_url', url, '--wda_port', port)
    else:
        raise Exception("{} is Not Supported Platform".format(_platform))
    return _main(*args)