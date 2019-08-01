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
import json
import pyautogui
import tkinter as tk
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


################################################################################
@func_log
def user_params(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: True
    """
    entries = list()

    # 버튼 콜백
    def button_clicked(v):
        data = dict()
        value = list()
        for l, e, d in entries:
            value.append((l, e.get(), d))
        data['show'] = {0: True, 1: False}[do_not_show_next.get()]
        data['action'] = v
        data['group'] = argspec.group
        data['values'] = value
        # 아래와 같은 결과 반환
        # {"show": False,
        #  "action": "ONCE",
        #  "values": [["{{ABC.DEF}}", "123", "DESC], ["{{ABC.GHI}}", "456", "DE"],
        #             ["{{ABC.XYZ}}", "789","DE"]]}
        sys.stdout.write(json.dumps(data))
        root.destroy()

    mcxt.logger.info('>>>')
    pyautogui.FAILSAFE = False

    root = tk.Tk()
    root.title("Dialogue")

    # Popup Title ==============================================================
    tk.Label(root, text=argspec.group,
             wraplength=300, width=50, height=10).pack(side='top')

    # Entry 생성 ===============================================================
    for i, q in enumerate(argspec.input):
        frame = tk.Frame(root)
        frame.pack()
        tk.Label(frame, text=q[0]).grid(row=0, column=0)
        le = tk.Entry(frame)
        le.insert(0, q[1])
        le.grid(row=0, column=1)
        tk.Label(frame, text=q[2]).grid(row=0, column=2)
        entries.append((q[0], le, q[2]))

    frame = tk.Frame(root)
    frame.pack()

    do_not_show_next = tk.IntVar()
    tk.Checkbutton(
        frame, text="Do not show next",
        variable=do_not_show_next, activebackground="blue").grid(row=0, column=0)
    tk.Button(
        frame, text="Continue to use",
        overrelief="solid", width=15,
        command=lambda: button_clicked('CONTINUE'),
        repeatdelay=1000, repeatinterval=100).grid(row=1, column=0)
    tk.Button(
        frame, text="Only once",
        overrelief="solid", width=15,
        command=lambda: button_clicked('ONCE'),
        repeatdelay=1000, repeatinterval=100).grid(row=1, column=1)

    # Gets the requested values of the height and width
    win_w = root.winfo_reqwidth()
    wind_h = root.winfo_reqheight()
    # Gets both half the screen width/height and window width/height
    pos_x = int(root.winfo_screenwidth() / 2 - win_w / 2)
    pos_y = int(root.winfo_screenheight() / 2 - wind_h / 2)
    # Positions the window in the center of the page.
    root.geometry("+{}+{}".format(pos_x, pos_y))

    root.mainloop()
    mcxt.logger.info('>>>end...')

    # print(json.dumps(SELECTED_BUTTON_VALUE))

    return

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
        "group_name" --input "variable_name" "default value" "description"
        """
        mcxt.add_argument('-i', '--input', action='append', nargs='+',
                          help=help_msg)

        ########################################################################
        mcxt.add_argument('group', type=str)
        argspec = mcxt.parse_args(args)
        return mcxt, argspec


################################################################################
def main(*args):
    mcxt, argspec = _main(*args)

    return user_params(mcxt, argspec)
