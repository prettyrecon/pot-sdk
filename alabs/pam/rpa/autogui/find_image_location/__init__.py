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
import pyautogui

from alabs.pam.utils.graphics import xywh_to_x1y1x2y2
from alabs.pam.utils.graphics import draw_box_with_title
from alabs.pam.utils.graphics import RGB



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
def find_all(target, image, save_filename=None, region=None, confidence=0.50,
             limit=1000, logger=None):

    locations = pyautogui.locateAll(target, image,
                                    region=region,
                                    confidence=confidence, limit=limit)

    x1, y1, x2, y2 = xywh_to_x1y1x2y2(region)
    draw_box_with_title(image, "Search Area", (x1, y1, x2, y2),
                        b_rgb=RGB.CHARTREUSE1.value,
                        box_thickness=2)

    if not locations:
        raise ValueError("Failed to find the images")

    # 좌표 x의 값이 0과 가까운 순서대로 먼저 정렬
    # 좌표 y의 값이 0에 가까운 순서대로 정렬
    locations = sorting(list(locations))

    for i, l in enumerate(locations, 1):
        x1, y1, x2, y2 = xywh_to_x1y1x2y2(l)
        # 선택된
        draw_box_with_title(image, f'{i}', (x1, y1, x2, y2))


    return locations


################################################################################
def sorting(data):
    """
    >>> a = [(1,1), (2, 1), (1,2), (1,3),(1,4),(2,4),(3,1),(2,2)]
    >>> b = sorting(a)
    >>> assert a == b

    # [(1, 1), (1, 2), (1, 3), (1, 4), (2, 1), (2, 3), (2, 4), (3, 1)]
    :param data:
    :return:
    """
    data.sort(key=lambda element: element[0])
    return data


################################################################################
def main(*args):
    _platform = os.environ.get('ARGOS_RPA_PAM_PLATFORM', platform.system())
    if _platform == 'Linux':
        from alabs.pam.rpa.autogui.find_image_location.linux import main as _main
    elif _platform == 'Windows':
        from alabs.pam.rpa.autogui.find_image_location.linux import main as _main
    elif _platform == 'Darwin':
        from alabs.pam.rpa.autogui.find_image_location.macos import main as _main

    elif _platform == 'iOS':
        from alabs.pam.rpa.autogui.find_image_location.ios import main as _main

    else:
        raise Exception("{} is Not Supported Platform".format(_platform))
    return _main(*args)


