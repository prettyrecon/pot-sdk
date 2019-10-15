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
# from win32gui import FindWindow
import win32gui
import psutil
import win32con
from alabs.common.util.vvargs import ModuleContext, func_log, str2bool, \
    ArgsError, ArgsExit
from pathlib import Path

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
@func_log
def select_window(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: actual delay seconds
    """
    mcxt.logger.info('>>>starting...')
    #print(argspec)
    process_name = argspec.name
    process_title = argspec.title
    if not process_name or not process_title:
        return

    process_name = check_process_name(process_name)  # 프로세스명에 .exe 붙이기

    handle = win32gui.FindWindow(process_name, process_title)  # 방법.1
    if handle == 0:
        handle = find_window_handle(process_name, process_title)  # 방법.2, 방법.3

    if handle == 0:
        return

    if argspec.location is not None:
        move_window(handle, argspec.location[0], argspec.location[1])  # 위치 조정
    if argspec.size is not None:
        change_window_size(handle, argspec.size[0], argspec.size[1])   # 사이즈 조정
    active_window(handle)  # 포커스
    # 클릭은 다른곳에서?
    mcxt.logger.info('>>>end...')
    return


def find_window_handle(name, title):
    handle = 0
    processes = get_processes_by_name(name)

    #브라우저 프로세스 체크
    is_browser = check_browser_process(name)
    if is_browser: #브라우저 프로세스일경우 타이틀값의 - 우측값 제거
        last_index = title.rfind('-')
        if last_index > 0:
            temp_strings = title.split('-')
            if len(temp_strings[len(temp_strings) - 1]) > 0:
                title = title[0:last_index].rstrip()

    for process in processes:  # 방법.2
        temp_handle = find_window_in_process(process, title, is_browser)
        if temp_handle != 0:
            handle = temp_handle
            break

    #  방법.3 프로세스에 스레드 개수가 1개일때 타이틀명으로 찾기
    if handle == 0:
        handle = win32gui.FindWindow(0, title)
    return handle


def get_processes_by_name(name):
    return [process for process in psutil.process_iter() if process.name() == name]


def find_window_in_process(process, title_pattern, is_browser):
    handle = 0
    for process_thread in process.threads():
        handle = find_window_in_thread(process_thread.id, title_pattern, is_browser)
        if handle != 0:
            return handle
    return handle


def find_window_in_thread(thread_id, title_pattern, is_browser):
    handle = 0

    def callback(window_handle, lparam):
        nonlocal handle
        if handle != 0: # False 로 리턴하지 못하여... 대체하여 처리
            return True
        window_style = win32gui.GetWindowLong(window_handle, win32con.GWL_STYLE)
        is_visible_window = (window_style & win32con.WS_VISIBLE) == win32con.WS_VISIBLE
        if is_visible_window == 0:
            return True
        title_string = win32gui.GetWindowText(window_handle)

        #웹일경우 타이틀 뒤쪽 -를 포함하여 모두 제거한후 비교
        if is_browser:
            last_index = title_string.rfind('-')
            if last_index > 0:
                temp_strings = title_string.split('-')
                if len(temp_strings[len(temp_strings) - 1]) > 0:
                    title_string = title_string[0:last_index].rstrip()

        # 와일드 카드를 적용한 타이틀비교. 같을 경우 핸들값 리턴
        if text_compare_with_wildcard(title_string, title_pattern):
            handle = window_handle
            return True #원래는 False 로 리턴해야하나... 에러가 발생함???? 이유는 모르겠음
        return True

    win32gui.EnumThreadWindows(thread_id, callback, 0)
    return handle


def active_window(handle):
    window_state_tuple = win32gui.GetWindowPlacement(handle)  # 창의 스타일값 가져오기
    if window_state_tuple[1] == win32con.SW_SHOWMINIMIZED:  # 창이 최소화 상태일경우
        win32gui.ShowWindow(handle, win32con.SW_RESTORE)  # 창을 RESTORE 상태로 변경
    win32gui.SetWindowPos(handle, win32con.HWND_TOP, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    win32gui.SetForegroundWindow(handle)  # 포커스
    return


def move_window(handle, x, y):
    win32gui.SetWindowPos(handle, win32con.HWND_TOP, x, y, 0, 0, win32con.SWP_NOSIZE)
    return


def change_window_size(handle, w, h):
    win32gui.SetWindowPos(handle, win32con.HWND_TOP, 0, 0, w, h, win32con.SWP_NOMOVE)
    return


def check_browser_process(process_name):
    if process_name is "chrome.exe" or "iexplore.exe" or "firefox.exe":
        return True
    return False


def check_process_name(process_name):  # c#에서는 프로세스명에 .exe를 제거해서 하였으나 python은 필요함.
    temp_process_name = process_name
    if not process_name.endswith('.exe'):
        temp_process_name = process_name + '.exe'
    return temp_process_name


def text_compare_with_wildcard(origin_text, pattern):
    if not origin_text or not pattern:
        return False
    temp_string = origin_text
    if '*' in pattern:
        dividers = pattern.split('*')

        if dividers[0] != "":
            is_result = temp_string.startswith(dividers[0])
            temp_string = temp_string.replace(dividers[0], "")
            if not is_result:
                return False

        while_index = 1
        while while_index < len(dividers):
            if dividers[while_index] == "":
                while_index += 1
                continue
            if while_index == len(dividers) - 1:
                is_result = temp_string.endswith(dividers[while_index])
            else:
                n_index = temp_string.find(dividers[while_index])
                is_result = n_index > -1
                if is_result:
                    temp_string = temp_string[n_index + len(dividers[while_index]):]
            if not is_result:
                return False
            while_index += 1

    return True


################################################################################
def _main(*args):
    with ModuleContext(
        owner=OWNER,
        group=GROUP,
        version=VERSION,
        platform=PLATFORM,
        output_type=OUTPUT_TYPE,
        description=DESCRIPTION,
    ) as mcxt:
        # select_window 'Untitled' 'Notepad.exe'
        # select_window 'Untitled' 'Notepad.exe' -l 10 20
        # select_window 'Untitled' 'Notepad.exe' -s 100 200
        # select_window 'Untitled' 'Notepad.exe' -c 110 210

        mcxt.add_argument('title', type=str, help='App Title')
        mcxt.add_argument('name', type=str, help='App Name')
        mcxt.add_argument('-l', '--location', nargs=2, type=int,
                          help='Set Location')
        mcxt.add_argument('-s', '--size', nargs=2, type=int,
                          help='Set Size')
        mcxt.add_argument('-c', '--click', nargs=2, type=int,
                          help='Click Point')
        argspec = mcxt.parse_args(args)
        return select_window(mcxt, argspec)

################################################################################
def main(*args):
    return _main(*args)