#!/usr/bin/env python
# coding=utf8
# noinspection PyBroadException
"""
====================================
 :mod:`alabs.util.vvlogger` 로그 (로거) 관련 함수
====================================
.. moduleauthor:: 채문창 <mcchae@alabs.net>
.. note:: MIT License
"""

# 설명
# =====
#
# 파일에 로그 및 로거를 위한 기능
#
# 관련 작업자
# ===========
#
# 본 모듈은 다음과 같은 사람들이 관여했습니다:
#  * 채문창
#
# 작업일지
# --------
#
# 다음과 같은 작업 사항이 있었습니다:
#  * [2017/04/10]
#       - 본 모듈 작업 시작

################################################################################
import os
import sys
import logging
import datetime
import logging.handlers
import traceback
from functools import wraps

################################################################################
__author__ = "MoonChang Chae <mcchae@alabs.net>"
__date__ = "2017/04/10"
__version__ = "1.17.0410"
__version_info__ = (1, 17, 410)
__license__ = "MIT"


################################################################################
def get_logger(logfile,
               logsize=500*1024, logbackup_count=4,
               logger=None, loglevel=logging.DEBUG):
    loglevel = loglevel
    if logger is None:
        logger = logging.getLogger(os.path.basename(logfile))
    logger.setLevel(loglevel)
    if logger.handlers is not None and len(logger.handlers) >= 0:
        for handler in logger.handlers:
            logger.removeHandler(handler)
        logger.handlers = []
    loghandler = logging.handlers.RotatingFileHandler(
        logfile,
        maxBytes=logsize, backupCount=logbackup_count,
        encoding='utf8')
    # else:
    #     loghandler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s-%(name)s-%(levelname)s-'
        '%(filename)s:%(lineno)s-[%(process)d] %(message)s')
    loghandler.setFormatter(formatter)
    logger.addHandler(loghandler)
    return logger


################################################################################
def get_traceback_str():
    """파이썬 디폴트 오류 스택 대신 출력할 문자열
        * 참고 <http://mcchae.egloos.com/11018564>
    :return: str 오류 스택 출력 문자열
    """
    lines = traceback.format_exc().strip().split('\n')
    rl = [lines[-1]]
    lines = lines[1:-1]
    lines.reverse()
    nstr = ''
    for i in range(len(lines)):
        line = lines[i].strip()
        if line.startswith('File "'):
            eles = lines[i].strip().split('"')
            basename = os.path.basename(eles[1])
            lastdir = os.path.basename(os.path.dirname(eles[1]))
            eles[1] = '%s/%s' % (lastdir, basename)
            rl.append('^\t%s %s' % (nstr, '"'.join(eles)))
            nstr = ''
        else:
            nstr += line
    rs = '\n'.join(rl)
    if rs == 'None':
        return None
    return rs


################################################################################
def method_log(original_function):
    @wraps(original_function)
    # ==========================================================================
    def new_function(self, *args, **kwargs):
        """ new_function for decorator """
        _s_ts_ = datetime.datetime.now()
        try:
            self.logger.debug('%s.%s(%s,%s) starting...' %
                              (type(self).__name__,
                               original_function.__name__, args, kwargs))
            r = original_function(self, *args, **kwargs)
            self.logger.debug('%s.%s(%s,%s) return:%s' %
                              (type(self).__name__,
                               original_function.__name__, args, kwargs, r))
            return r
        except Exception as exp:
            self.logger.error('%s.%s(%s,%s):Error:%s' %
                              (type(self).__name__,
                               original_function.__name__, args, kwargs,
                               str(exp)))
            _exc_info = sys.exc_info()
            _out = traceback.format_exception(*_exc_info)
            del _exc_info
            self.logger.error("'%s.%s(%s,%s):Error Stack: %s" %
                              (type(self).__name__,
                               original_function.__name__, args, kwargs,
                               ''.join(_out)))
            raise  # current exception
        finally:
            _e_ts_ = datetime.datetime.now()
            self.logger.debug('%s.%s(%s,%s) takes:%s' %
                              (type(self).__name__,
                               original_function.__name__, args, kwargs,
                               (_e_ts_ - _s_ts_)))
    # ==========================================================================
    # enherit from original_function
    return new_function


################################################################################
def do_except(cnt=3):
    """do_test에서 시험용으로 호출할 재귀함수
        3번의 재귀호출 후 ValueError 예외 발생시킴
    """
    if cnt < 0:
        raise ValueError('cnt is below zero')
    else:
        do_except(cnt-1)

