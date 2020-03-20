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

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import cv2
# from tesserocr import PyTessBaseAPI
# from tesserocr import PyTessBaseAPI, RIL, iterate_level, PSM, OEM


import pathlib
from alabs.common.util.vvargs import ModuleContext
from alabs.common.util.vvlogger import StructureLogFormat


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


def image_preprocessing(image_path, gaussianblur=None, threshold=None,
                        edgepreserv=None):
    # 이미지 처리
    img = cv2.imread(image_path)

    # 가우시안 블러처리
    if gaussianblur:
        w, h = gaussianblur
        # 양의 홀수 값만 처리
        cv2.GaussianBlur(img, (int(w), int(h)), 0)

    if threshold:
        low, high, threshold_type = threshold
        th_type = {'Binary': cv2.THRESH_BINARY,
                   'BinaryInv': cv2.THRESH_BINARY_INV,
                   'Trunc': cv2.THRESH_TRUNC,
                   'Tozero': cv2.THRESH_TOZERO,
                   'TozeroInv': cv2.THRESH_TOZERO_INV,
                   'Mask': cv2.THRESH_MASK,
                   'Otsu': cv2.THRESH_OTSU,
                   'Triangle': cv2.THRESH_TRIANGLE}

        cv2.threshold(img, int(low), int(high), th_type[threshold_type])

    if edgepreserv:
        cv2.edgePreservingFilter(img)

    return img


################################################################################
def tesseract(tesseract_path, image, tessdata_path=None,  digit_only=False,
              remove_space=False):
    config = list()
    pytesseract.pytesseract.tesseract_cmd = r'{}'.format(tesseract_path)

    # 트래이닝 데이터 위치
    if not tessdata_path:
        tessdata_path = pathlib.WindowsPath(tesseract_path).parents[0] / \
                       pathlib.WindowsPath('tessdata')
        tessdata_path = str(tessdata_path)
    config.append(r'--tessdata-dir "{}"'.format(tessdata_path))

    if digit_only:
        config.append("-c tessedit_char_whitelist=0123456789-.")
    config = ' '.join(config)

    data = pytesseract.image_to_string(image, config=config)

    if remove_space:
        data = data.replace(' ', '')

    return data


def tesseract_ocr():
    result = list()
    # with PyTessBaseAPI() as api:
    with PyTessBaseAPI(path=tessdata_dir, lang='eng') as api:
        im_pil = Image.fromarray(img)
        # api.SetVariable("save_blob_choices", "T")
        api.SetImage(im_pil)
        api.Recognize()

        text = api.GetUTF8Text()
        text = list(text)
        ri = api.GetIterator()
        level = RIL.SYMBOL

        ri = iterate_level(ri, level)
        text = iter(text)
        r = next(ri)
        for i, t in enumerate(text):
            try:
                print(t)
                if r.GetUTF8Text(level) == t:
                    d = r

                    x1, y1, x2, y2 = d.BoundingBox(level)
                    if y2 - y1 < 20:
                        pass
                    else:
                        symbol = d.GetUTF8Text(level)
                        result.append(symbol)
                    r = next(ri)
                else:
                    result.append(t)
                    continue
            except StopIteration:
                t = next(text)
                result.append(t)
                break


################################################################################
def ocr(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: True
    """

    image = image_preprocessing(image_path=argspec.image_path,
                                gaussianblur=argspec.gaussianblur,
                                threshold=argspec.threshold,
                                edgepreserv=argspec.edgepreserv)
    data = tesseract(tesseract_path=argspec.tesseract_path,
                     image=image,
                     tessdata_path=argspec.tessdata,
                     digit_only=argspec.digit_only,
                     remove_space=argspec.remove_space)

    result = StructureLogFormat(RETURN_CODE=True, RETURN_VALUE=data, MESSAGE="")
    sys.stdout.write(str(result))
    return result


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
        ########################################################################

        mcxt.add_argument('tesseract_path', type=str,
                          help='The location of Tesseract')
        mcxt.add_argument('image_path', type=str,
                          help='The target image file for OCR')
        mcxt.add_argument('--lang', type=str, default='eng')
        mcxt.add_argument('--digit_only', action='store_true')
        mcxt.add_argument('--gaussianblur', nargs=2, type=int)
        mcxt.add_argument('--threshold', nargs=3, type=str,
                          help='low_gray_tone high_gray_tone type')
        mcxt.add_argument('--tessdata', type=str, default='',
                          help='')
        mcxt.add_argument('--edgepreserv', action='store_true')
        mcxt.add_argument('--minimum', type=int, default=0)
        mcxt.add_argument('--remove_space', action='store_true')
        argspec = mcxt.parse_args(args)
        return ocr(mcxt, argspec)


################################################################################
def main(*args):
    return _main(*args)

