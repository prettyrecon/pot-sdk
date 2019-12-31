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
import platform
#

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
def main(*args):
    _platform = os.environ.get('ARGOS_RPA_PAM_PLATFORM', platform.system())
    if _platform == 'Linux':
        raise NotImplemented
        # from alabs.pam.rpa.desktop.select_window.linux import main as _main

    elif _platform == 'Windows':
        from alabs.pam.rpa.desktop.select_window.windows import main as _main

    elif _platform == 'Darwin':
        # from alabs.pam.rpa.desktop.select_window.windows import main as _main
        raise NotImplemented
        # from alabs.pam.rpa.desktop.select_window.linux import main as _main

    elif _platform == 'IOS':
        raise NotImplemented
        # from alabs.pam.rpa.autogui.click.ios import main as _main
        # return _main('--wda_url', url, '--wda_port', port)
    else:
        raise Exception("{} is Not Supported Platform".format(_platform))
    return _main(*args)

