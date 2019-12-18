"""
====================================
 :mod:`argoslabs.demo.helloworld`
====================================
.. moduleauthor:: Raven Lim <deokyu@argos-labs.com>
.. note:: VIVANS License

Description
===========
ARGOS LABS plugin module sample
"""

################################################################################
import sys
import multiprocessing
from alabs.common.util.vvargs import ArgsError, ArgsExit
from alabs.pam import _main


################################################################################
if __name__ == '__main__':
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()
    try:
        _main()
    except ArgsError as err:
        sys.stderr.write('Error: %s\nPlease -h to print help\n' % str(err))
    except ArgsExit as _:
        pass
