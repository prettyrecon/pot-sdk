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
import sys
import json
import win32gui
import psutil
import win32con
from alabs.common.util.vvlogger import StructureLogFormat
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
    창에 포커스를 주는 기능. 옵션으로 위치, 사이즈 조절
    -l 100 200 : 창의 위치를 100, 200 위치로 이동
    -s 600 400 : 창의 크기를 600 x 400 크기로 변경
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: window position and size (x, y, width, height)
    """
    mcxt.logger.info('>>>starting...')
    # print(argspec)
    process_name = argspec.name
    process_title = argspec.title
    if not process_name or not process_title:
        sys.stderr.write(
            str(StructureLogFormat(RETURN_CODE=False, RETURN_VALUE=None,
                                   MESSAGE="No title or process name.")))
        return

    # 입력한 프로세스명에 .exe 가 없을경우 .exe 붙이기
    process_name = check_process_name(process_name)

    # 방법.1 win32api 함수를 이용하여 창의 handle 값 가져오기
    handle = win32gui.FindWindow(process_name, process_title)

    # 방법.2  특정 name 의 프로세스 내에서 title 을 비교해서 찾기
    # 방법.3  모든 프로세스내에서 title 을 비교해서 찾기
    if handle == 0:
        handle = find_window_handle(process_name, process_title)

    # handle 을 찾지 못했을 경우 리턴
    if handle == 0:
        sys.stderr.write(
            str(StructureLogFormat(RETURN_CODE=False, RETURN_VALUE=None,
                                   MESSAGE="Couldn't find the handle.")))
        exit(-1)

    if argspec.location is not None:
        # 위치 조정
        move_window(handle, argspec.location[0], argspec.location[1])
    if argspec.size is not None:
        # 사이즈 조정
        change_window_size(handle, argspec.size[0], argspec.size[1])
    # 포커스
    active_window(handle)

    # 윈도우의 위치 사이즈 정보를 리턴
    result = get_window_rect(handle)
    data = StructureLogFormat(RETURN_CODE=True, RETURN_VALUE=result,MESSAGE='')
    sys.stdout.write(str(data))
    mcxt.logger.info(result)
    mcxt.logger.info('>>>end...')
    return data


################################################################################
def find_window_handle(name, title):
    """
    특정 name 의 프로세스 내에서 title 에 해당하는 window handle 리턴
    :param name: process name
    :param title: window title
    :return: window handle
    """
    handle = 0
    processes = get_processes_by_name(name)

    # 브라우저 프로세스 체크
    is_browser = check_browser_process(name)
    # 브라우저 프로세스일경우 타이틀값의 - 를 포함한 우측값 제거
    if is_browser:
        last_index = title.rfind('-')
        if last_index > 0:
            temp_strings = title.split('-')
            if len(temp_strings[len(temp_strings) - 1]) > 0:
                title = title[0:last_index].rstrip()

    for process in processes:
        # 방법.2
        temp_handle = find_window_in_process(process, title, is_browser)
        if temp_handle != 0:
            handle = temp_handle
            break

    #  방법.3 프로세스에 스레드 개수가 1개일때 타이틀명으로 찾기
    if handle == 0:
        handle = win32gui.FindWindow(0, title)
    return handle


################################################################################
def get_processes_by_name(name):
    """
    특정 name 의 모든 프로세스를 리턴
    :param name: process name
    :return: process list
    """
    return [process for process
            in psutil.process_iter() if process.name() == name]


################################################################################
def find_window_in_process(process, title_pattern, is_browser):
    """
    프로세스 내에서 title_pattern 에 해당하는 window handle 을 찾는다.
    :param process: 프로세스명
    :param title_pattern: 찾을 title
    :param is_browser: 브라우저 프로세스 여부 (True, False)
    :return: window handle
    """
    handle = 0
    for process_thread in process.threads():
        handle = find_window_in_thread(process_thread.id,
                                       title_pattern, is_browser)
        if handle != 0:
            return handle
    return handle


################################################################################
def find_window_in_thread(thread_id, title_pattern, is_browser):
    """
    특정 thread id에 해당하는 창들 중에서 타이틀에 해당하는 handle 을 찾는다
    :param thread_id: thread id
    :param title_pattern: 찾을 title
    :param is_browser: 브라우저 프로세스 여부 (True, False)
    :return: window handle
    """
    handle = 0

    def callback(window_handle, lparam):
        nonlocal handle
        if handle != 0:  # False 로 리턴하지 못하여... 대체하여 처리
            return True
        window_style = \
            win32gui.GetWindowLong(window_handle, win32con.GWL_STYLE)
        is_visible_window = \
            (window_style & win32con.WS_VISIBLE) == win32con.WS_VISIBLE
        if is_visible_window == 0:
            return True
        title_string = win32gui.GetWindowText(window_handle)

        # 웹일경우 타이틀 뒤쪽 -를 포함하여 모두 제거한후 비교
        if is_browser:
            last_index = title_string.rfind('-')
            if last_index > 0:
                temp_strings = title_string.split('-')
                if len(temp_strings[len(temp_strings) - 1]) > 0:
                    title_string = title_string[0:last_index].rstrip()

        # 와일드 카드를 적용한 타이틀비교. 같을 경우 핸들값 리턴
        if text_compare_with_wildcard(title_string, title_pattern):
            handle = window_handle
            return True  # False 로 리턴해야하나.. 에러발생, 이유는 모르겠음
        return True

    win32gui.EnumThreadWindows(thread_id, callback, 0)
    return handle


################################################################################
def active_window(handle):
    """
    특정 handle 의 창을 활성화(포커스)
    :param handle: window handle
    :return: None
    """
    # 창의 스타일값 가져오기
    window_state_tuple = win32gui.GetWindowPlacement(handle)
    # 창이 최소화 상태일경우
    if window_state_tuple[1] == win32con.SW_SHOWMINIMIZED:
        # 창을 RESTORE 상태로 변경
        win32gui.ShowWindow(handle, win32con.SW_RESTORE)
    # 창 상태를 TOP 으로 변경
    win32gui.SetWindowPos(handle, win32con.HWND_TOP, 0, 0, 0, 0,
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    # 창을 포커스 상태로 변경
    win32gui.SetForegroundWindow(handle)
    return


################################################################################
def move_window(handle, x, y):
    """
    특정 handle 의 창 위치를 변경
    :param handle: window handle
    :param x: location x
    :param y: location y
    :return: None
    """
    win32gui.SetWindowPos(
        handle, win32con.HWND_TOP, x, y, 0, 0, win32con.SWP_NOSIZE)
    return


################################################################################
def change_window_size(handle, w, h):
    """
    특정 handle 의 창 크기를 변경
    :param handle: window handle
    :param w: width value
    :param h: height value
    :return: None
    """
    win32gui.SetWindowPos(
        handle, win32con.HWND_TOP, 0, 0, w, h, win32con.SWP_NOMOVE)
    return


################################################################################
def check_browser_process(process_name):
    """
    프로세스명으로 브라우저 프로세스인지 체크
    :param process_name: .exe 가 포함된 프로세스명
    :return: 브라우저 프로세스일 경우 True, 아니면 False
    """
    if process_name is "chrome.exe" or "iexplore.exe" or "firefox.exe":
        return True
    return False


################################################################################
def check_process_name(process_name):
    """
    프로세스명에 .exe 가 없을경우 문자열을 추가하여 리턴
    c#에서는 프로세스명에 .exe를 제거해서 하였으나 python은 필요함.
    :param process_name:
    :return: .exe 가 포함된 프로세스 이름을 리턴 (ex : notepad.exe)
    """
    temp_process_name = process_name
    if not process_name.endswith('.exe'):
        temp_process_name = process_name + '.exe'
    return temp_process_name


################################################################################
def text_compare_with_wildcard(origin_text, pattern):
    """
    원문과 패턴을 비교하여 유사한값이면 True 다른값이면 False 를 리턴
    원문이 Hello 일때 다음과 같을경우 모두 True
    ex) *Hello* , Hel* , H*o , *
    :param origin_text: 원문 문자열
    :param pattern: 비교할 문자열 또는 * 가 포함된 문자열
    :return: True 같거나 유사한 값일때, False 다른값 일때
    """
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
                    temp_string = \
                        temp_string[n_index + len(dividers[while_index]):]
            if not is_result:
                return False
            while_index += 1

    return True


################################################################################
def get_window_rect(handle):
    """
    특정 handle 의 창 위치와 크기값을 리턴
    :param handle: window handle
    :return: x좌표,y좌표,폭,높이
    """
    result = win32gui.GetWindowRect(handle)
    location_string = '%s,%s' % (result[0], result[1])
    size_string = '%s,%s' % (result[2] - result[0], result[3] - result[1])
    return location_string + ',' + size_string


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
        # mcxt.add_argument('-c', '--click', nargs=2, type=int,
        #                   help='Click Point')
        argspec = mcxt.parse_args(args)
        return select_window(mcxt, argspec)

################################################################################
def main(*args):
    return _main(*args)