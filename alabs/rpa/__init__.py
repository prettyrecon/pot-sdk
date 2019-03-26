import sys
import os

ENV_ARCHITECTURE = 'ARGOS_ARCHITECTURE'
arch = os.getenv(ENV_ARCHITECTURE, None)
arch = 'HA'
if arch == 'LA':
    from alabs.rpa.la.desktop.execute_process import main as _execute_process
    from alabs.rpa.la.desktop.stop_process import main as _stop_process
    from alabs.rpa.la.desktop.delete_file import main as _delete_file
    from alabs.rpa.la.desktop.delay import main as _delay
    from alabs.rpa.la.desktop.select_window import main as _select_window

    # AUTOGUI
    from alabs.rpa.la.autogui.find_image_location import main as \
        _find_image_location
    from alabs.rpa.la.autogui.locate_image import main as _locate_image
    from alabs.rpa.la.autogui.click import main as _click
    from alabs.rpa.la.autogui.scroll import main as _scroll
    from alabs.rpa.la.autogui.send_shortcut import main as _send_shortcut
    from alabs.rpa.la.autogui.type_text import main as _type_text

    pass
elif arch == 'HA':
    # DESKTOP
    from alabs.rpa.ha.desktop.execute_process import main as _execute_process
    from alabs.rpa.ha.desktop.stop_process import main as _stop_process
    from alabs.rpa.ha.desktop.delete_file import main as _delete_file
    from alabs.rpa.ha.desktop.delay import main as _delay
    from alabs.rpa.ha.desktop.select_window import main as _select_window

    # AUTOGUI
    from alabs.rpa.ha.autogui.find_image_location import main as \
        _find_image_location
    from alabs.rpa.ha.autogui.locate_image import main as _locate_image
    from alabs.rpa.ha.autogui.click import main as _click
    from alabs.rpa.ha.autogui.scroll import main as _scroll
    from alabs.rpa.ha.autogui.send_shortcut import main as _send_shortcut
    from alabs.rpa.ha.autogui.type_text import main as _type_text

    # AUTOREC

else:
    raise NotImplementedError('** NOT SUPPORTED ARCHITECTURE **')


################################################################################
# DESKTOP
################################################################################
def execute_process(*args):
    return _execute_process(*args)

def stop_process(*args):
    return _stop_process(*args)

def delete_file(*args):
    return _delete_file(*args)

def delay(*args):
    return _delay(*args)

def select_window(*args):
    return _select_window(*args)


################################################################################
# AUTOGUI
################################################################################
def find_image_location(*args):
    return _find_image_location(*args)

def locate_image(*args):
    return _locate_image(*args)

def click(*args):
    return _click(*args)

def scroll(*args):
    return _scroll(*args)

def send_shortcut(*args):
    return _send_shortcut(*args)

def type_text(*args):
    return _type_text(*args)










