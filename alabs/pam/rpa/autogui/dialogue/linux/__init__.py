#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod:`alabs.pam.la.bot2py
====================================
.. moduleauthor:: Raven Lim <deokyu@argos-labs.com>
.. note:: VIVANS License

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
import sys
import pickle
import json
import pyautogui
import tkinter as tk
from .. import check_args, Action
from alabs.common.util.vvargs import ModuleContext, func_log



################################################################################
# Version
NUM_VERSION = (0, 9, 0)
VERSION = ".".join(str(nv) for nv in NUM_VERSION)
__version__ = VERSION

OWNER = 'ARGOS-LABS'
GROUP = 'Pam'
PLATFORM = ['windows', 'darwin', 'linux']
OUTPUT_TYPE = 'json'
DESCRIPTION = 'Pam for HA. It reads json scenario files by LA Stu and runs'

SELECTED_BUTTON_VALUE = None

################################################################################
# @func_log
def dialogue(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: True
    """

    # 버튼 콜백
    def button_clicked(v):
        global SELECTED_BUTTON_VALUE
        SELECTED_BUTTON_VALUE = v
        sys.stdout.write(','.join(SELECTED_BUTTON_VALUE))
        root.destroy()

    pyautogui.FAILSAFE = False

    root = tk.Tk()
    frame = tk.Frame(root)
    frame.pack(side="bottom")

    # 버튼 생성
    mcxt.logger.info(str(argspec.button))
    for i, button in enumerate(argspec.button):
        tk.Button(
            frame, text=button[Action.TITLE],
            overrelief="solid", width=15,
            command=lambda button=button: button_clicked(button),
            repeatdelay=1000, repeatinterval=100).grid(row=0, column=i)

    root.title("Dialogue")

    # Gets the requested values of the height and width
    win_w = root.winfo_reqwidth()
    wind_h = root.winfo_reqheight()
    # Gets both half the screen width/height and window width/height
    pos_x = int(root.winfo_screenwidth() / 2 - win_w / 2)
    pos_y = int(root.winfo_screenheight() / 2 - wind_h / 2)
    # Positions the window in the center of the page.
    root.geometry("+{}+{}".format(pos_x, pos_y))

    # Popup Title
    tk.Label(root, text=argspec.title, wraplength=300,
             width=50, height=10).pack()
    # root.geometry()
    root.mainloop()
    return True


################################################################################
def _main(*args):
    """
    Build user argument and options and call plugin job function
    :param args: user arguments
    :return: return value from plugin job function

    ..note:: _main 함수에서 사용되는 패러미터(옵션) 정의 방법
플러그인 모듈은 ModuleContext 을 생성하여 mcxt를 with 문과 함께 사용
    owner='ARGOS-LABS',
    group='pam',
    version='1.0',
    platform=['windows', 'darwin', 'linux'],
    output_type='text',
    description='HA Bot for LA',
    test_class=TU,
    """
    with ModuleContext(
        owner=OWNER,
        group=GROUP,
        version=VERSION,
        platform=PLATFORM,
        output_type=OUTPUT_TYPE,
        description=DESCRIPTION,
    ) as mcxt:
        help_msg = """
        title --button Resume "title"
        title --button MoveOn "title"
        title --button TreatAsError "title"
        title --button IgnoreFailure "title"
        title --button AbortScenarioButNoError "title"

        title --button JumpForward "title" 3
        title --button JumpBackward "title" 3

        title --button JumpToOperation "title" op
        title --button JumpToStep "title" step

        title --button RestartFromTop "title"
        """
        mcxt.add_argument('-b', '--button', action='append', nargs='+',
                          help=help_msg)

        ########################################################################
        # mcxt.add_argument('coordinates', nargs=2, type=int, default=None,
        #                   metavar='COORDINATE', help='X Y')
        mcxt.add_argument('title', type=str)
        argspec = mcxt.parse_args(args)
        return mcxt, argspec


################################################################################
def main(*args):
    mcxt, argspec = _main(*args)
    # check_args(argspec)
    return dialogue(mcxt, argspec)
