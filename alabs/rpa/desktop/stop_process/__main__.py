"""
====================================
 :mod:`argoslabs.demo.helloworld`
====================================
.. moduleauthor:: Jerry Chae <mcchae@argos-labs.com>
.. note:: VIVANS License

Description
===========
ARGOS LABS plugin module sample
"""

################################################################################
import sys
from alabs.common.util.vvargs import ArgsError, ArgsExit
from alabs.rpa.ha.desktop.stop_process import main


################################################################################
if __name__ == '__main__':
    try:
        main()
    except ArgsError as err:
        sys.stderr.write('Error: %s\nPlease -h to print help\n' % str(err))
    except ArgsExit as _:
        pass