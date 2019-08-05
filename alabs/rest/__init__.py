#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod:`alabs.rest.__init__` rest basic functions and so on
====================================
.. moduleauthor:: 채문창 <mcchae@gmail.com>
.. note:: MIT
"""

# 설명
# =====
#
# rest service using Flask-RESTful
#
# RESTAPI (http://bcho.tistory.com/914)
# ==============================================================================
# |   리소스     |     POST     |     GET     |     PUT      |     DELETE        |
# +------------+--------------|--------------+-----------------+----------------
# |            |    create    |     read    |     update    |      delete      |
# +------------+--------------|-------------+---------------+------------------+
# | /{rces}    | 새로운rce 등록| rces목록리턴 | 여러rces bulk갱신|여러/모든 rces 삭제 |
# +------------+--------------|--------------+-----------------+---------------+
# |/{rces}/{id}|    에러   |{id}라는rce리턴 |{id} 라는 rce 갱신 |  {id} rce 삭제    |
# ==============================================================================
#
# The success Method : URI : actions are
# ==============================================================================
# HTTP Method  |               URI               |          Action             |
# +------------+---------------------------------+-----------------------------|
#    GET       | http://{host}/api/v1.0/rces     | retrieve list of rces (필터등)|
#    POST      | http://{host}/api/v1.0/rces     | create a new rce            |
#    DELETE    | http://{host}/api/v1.0/rces     | delete all rces (필터)       |
# +------------+---------------------------------+-----------------------------|
#    GET       | http://{host}/api/v1.0/rces/{id}| retrieve a rce              |
#    PUT       | http://{host}/api/v1.0/rces/{id}| update a rce                |
#    DELETE    | http://{host}/api/v1.0/rces/{id}| delete a rce                |
# ==============================================================================
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
#  * [2018/04/13]
#     - pickle 추가
#  * [2017/10/18]
#     - modify for flask-restplus
#  * [2017.04.27]
#     - 본 모듈 작업 시작

################################################################################
# noinspection PyPackageRequirements
import os
import sys
import json
# import urllib
import signal
import requests
import datetime
import hashlib
from tempfile import gettempdir
from random import randint
from urllib.parse import quote_plus
from uuid import uuid4
from alabs.common.util.vvjson import convert_str
# noinspection PyPackageRequirements
from flask import current_app
# from flask_login import current_user
# from functools import wraps
# from alabs.common.util.vvprint import PrettyPrinter
from requests.utils import requote_uri


################################################################################
# for constants of ns_pickle
################################################################################
REST_API_PREFIX = 'rest'
REST_API_NAME = 'rc_api'
REST_API_VERSION = 'v1.0'

################################################################################
# default LIMIT for get_all
################################################################################
DEFAULT_LIMIT = 100


################################################################################
def get_long_id():
    # 고유수를 구하는데 javascript에서는 Int 값에 제약이 있어 다음과 같이 & 시킴
    return uuid4().int & (2**53-1)


################################################################################
def get_keyval(res_id):
    if isinstance(res_id, (int,)):
        return '_uid', res_id
    if res_id.find('::=') > 0:
        return tuple(res_id.split('::='))
    raise RuntimeError('Invalid resource id')


################################################################################
def get_tempfile(root=gettempdir(), prefix='temp_', ext='tmp'):
    while True:
        fn = os.path.join(root, '%s%08d.%s'
                          % (prefix, randint(1, 99999999), ext))
        if not os.path.exists(fn):
            return fn


################################################################################
def cond_decorate(condition, decorator):
    def resdec(f):
        if not condition:
            return f
        return decorator(f)
    return resdec
    # return decorator if condition else lambda x: x


################################################################################
def get_passwd_hash(password):
    hash_object = hashlib.sha256(password.encode())
    return hash_object.hexdigest()


################################################################################
def receive_signal(signum, _):
    """시그널 핸들러
    """
    if signum in [signal.SIGTERM, signal.SIGHUP, signal.SIGINT]:
        current_app.logger.info('Caught signal %s, exiting.' % (str(signum)))
        sys.exit()
    else:
        current_app.logger.info('Caught signal %s, ignoring.' % (str(signum)))


# ################################################################################
# def make_safe_json(rec):
#     return convert_safe_str(rec)
#
#
# ################################################################################
# def response_to_str(r):
#     if isinstance(r, Response):
#         r_data = PrettyPrinter().pformat(r.data)
#         if len(str(r_data)) <= 256:
#             return '<<<%s%s>>>' % (r.status, r_data)
#         return '<<<%s%s...>>>' % (r.status, r_data[:256])
#     r_data = PrettyPrinter().pformat(r)
#     if len(r_data) <= 256:
#         return r_data
#     return '%s...' % r_data[:256]


################################################################################
def parse_req_data(request):
    """
    flask의 request에서 사용자 데이터를 가져옴
        주의: flask-restplus 모듈을 이용하여 swagger ui를 이용하는 패러미터
            패싱이 제대로 안되어 본 함수 이용 (0.10.1)
    :param request: Flask의 request
    :return: parameter dict
    """
    if not hasattr(request, 'method'):
        return None
    if request.method.upper() != 'GET':
        if request.data:
            req_data = request.data
            if isinstance(request.data, bytes):
                req_data = request.data.decode()
            return convert_str(json.loads(req_data))
    if 'json' in request.args:
        return convert_str(json.loads(request.args['json']))
    if request.args:
        return request.args     # note: type is ImmutableMultiDict
    return {}


################################################################################
class AuditLog(object):
    # ==========================================================================
    def __init__(self, where=None):
        self.where = where
        self.s_ts = datetime.datetime.now()
        self.userid = 'anonymous'
        self.status = 'OK'
        self.desc = "well done"
        self.elapsed = 0.0

    # ==========================================================================
    def add_where(self, where):
        if not self.where:
            self.where = where
        else:
            self.where += ' %s' % where

    # ==========================================================================
    def set_user(self, user):
        if user and hasattr(user, 'user_id') and user.user_id:
            self.userid = user.user_id

    # ==========================================================================
    def set_except(self, exp):
        self.status = 'Error'
        _desc = '[%s] %s' % (type(exp), str(exp))
        self.desc = _desc.replace("'", '').replace('\n', ' ')

    # # ========================================================================
    # def get_dict(self):
    #     _tdiff = datetime.datetime.now() - self.s_ts
    #     self.elapsed = _tdiff.seconds + _tdiff.microseconds / 1000000.0
    #     return {
    #         'where': self.where,
    #         'desc': self.desc,
    #         'status': self.status,
    #         'elapsed': self.elapsed,
    #         'userid': self.userid,
    #     }

    # ==========================================================================
    def save(self):
        _tdiff = datetime.datetime.now() - self.s_ts
        self.elapsed = _tdiff.seconds + _tdiff.microseconds / 1000000.0
        _audit_log = {
            'where': self.where,
            'desc': self.desc,
            'status': self.status,
            'elapsed': self.elapsed,
            'userid': self.userid,
        }
        sql = "INSERT INTO audits " \
              "(_where, userid, status, _desc, elapsed) " \
              "values " \
              "('{where}','{userid}','{status}','{desc}',{elapsed})"
        return current_app.orm.execute(sql, _audit_log)


# ################################################################################
# def audit_log(original_function):
#     @wraps(original_function)
#     # ======================================================================
#     def new_function(*args, **kwargs):
#         """ new_function for decorator """
#         _audit_log = None
#         try:
#             !!!  jsonify(json) is the reponse object
#             r = original_function(*args, **kwargs)
#             if 'audit_log' in r:
#                 _audit_log = r['audit_log']
#                 del r['audit_log']
#             return r
#         except Exception as exp:
#             raise  # current exception
#         finally:
#             if _audit_log:
#                 sql = "INSERT INTO audits " \
#                       "(_where, userid, status, _desc, elapsed) " \
#                       "values " \
#                       "('{where}','{userid}','{status}','{desc}',{elapsed})"
#                 current_app.orm.execute(sql, _audit_log)
#     # ======================================================================
#     # enherit from original_function
#     return new_function


################################################################################
class RestClient(object):
    """ Restful Client simulation class """
    # ==========================================================================
    def __init__(self, host, port, table, api_version='1.0',
                 api_name='api',
                 use_https=False, url_prefix=''):
        self.use_https = use_https
        proto = 'https' if use_https else 'http'
        self.url_base = '%s://%s:%s' % (proto, host, port)
        self.url_path = ''
        if url_prefix and url_prefix[-1] == '/':
            url_prefix = url_prefix[:-1]
        self.url_prefix = url_prefix
        self.api_name = api_name
        self.api_version = api_version
        self.session = requests.Session()
        self.set_resource(table)

    # ========================================================================
    def set_resource(self, table_or_func,
                     _prefix=None, _api_name=None, _api_version=None):
        url_prefix = self.url_prefix if not _prefix else _prefix
        api_name = self.api_name if not _api_name else _api_name
        api_version = self.api_version if not _api_version else _api_version
        if url_prefix:
            if url_prefix[-1] == '/':
                url_prefix = url_prefix[:-1]
            self.url_path = url_prefix
        else:
            self.url_path = ''
        if api_name:
            self.url_path += '/%s' % api_name
        if api_version:
            self.url_path += '/%s' % api_version
        if table_or_func:
            self.url_path += '/%s' % table_or_func
        if self.url_path.startswith('/'):
            self.url_path.lstrip('/')
        return True

    # ==========================================================================
    # def set_api_url(self, repository, table_or_func='foos'):
    #     # REST client use requests session so we need to chagne like this
    #     if repository == 'mongo':
    #         self.set_resource(table_or_func, MONGO_API_PREFIX,
    #                           MONGO_API_NAME, MONGO_API_VERSION)
    #     elif repository == 'mysql':
    #         self.set_resource(table_or_func, MYSQL_API_PREFIX,
    #                           MYSQL_API_NAME, MYSQL_API_VERSION)
    #     elif repository == 'aaa':
    #         self.set_resource(table_or_func, AAA_API_PREFIX,
    #                           AAA_API_NAME, AAA_API_VERSION)
    #     elif repository == 'pickle':
    #         self.set_resource(table_or_func, PICKLE_API_PREFIX,
    #                           PICKLE_API_NAME, PICKLE_API_VERSION)
    #     elif repository == 'file':
    #         self.set_resource(table_or_func, FILE_API_PREFIX,
    #                           FILE_API_NAME, FILE_API_VERSION)
    #     else:
    #         raise RuntimeError('API repository must be "mongo" '
    #                            'or "mysql" or "aaa"')
    #
    # ==========================================================================
    def get_all(self, where_json=None):
        """
        GET methos on .../Resouce on RESTful
        :param where_json:
        :return:
        """
        urlpath = self.url_path
        if where_json is None:
            where_json = {}
        return self.do_http("GET", urlpath, p_json=where_json,
                            use_param_url=True)

    # ==========================================================================
    def create(self, a_data):
        """
        POST methos on .../Resouce on RESTful
        :param a_data:
        :return:
        """
        urlpath = self.url_path
        return self.do_http("POST", urlpath, p_json=a_data)

    # ==========================================================================
    def update_all(self, set_json, where_json=None):
        """
        DELETE methos on .../Resouce on RESTful
        :param set_json:
        :param where_json:
        :return:
        """
        urlpath = self.url_path
        if where_json is None:
            where_json = {}
        if where_json:
            p_json = {'sets': set_json, 'filter': where_json}
        else:
            p_json = {'sets': set_json}
        return self.do_http("PUT", urlpath, p_json=p_json)

    # ==========================================================================
    def delete_all(self, where_json=None):
        """
        DELETE methos on .../Resouce on RESTful
        :param where_json:
        :return:
        """
        urlpath = self.url_path
        if where_json is None:
            where_json = {}
        return self.do_http("DELETE", urlpath, p_json=where_json)

    # ==========================================================================
    def get(self, resouce_id, p_json=None):
        """
        GET methos on .../Resouce/rid on RESTful
        :param resouce_id:
        :param p_json:
        :return:
        """
        urlpath = '%s/%s' % (self.url_path, resouce_id)
        if not p_json:
            return self.do_http("GET", urlpath)
        return self.do_http("GET", urlpath, p_json=p_json, use_param_url=True)

    # ==========================================================================
    def update(self, resouce_id, a_data):
        """
        PUT methos on .../Resouce/rid on RESTful
        :param resouce_id:
        :param a_data:
        :return:
        """
        urlpath = '%s/%s' % (self.url_path, resouce_id)
        return self.do_http("PUT", urlpath, a_data)

    # ==========================================================================
    def delete(self, resouce_id):
        """
        DELETE methos on .../Resouce/rid on RESTful
        :param resouce_id:
        :return:
        """
        urlpath = '%s/%s' % (self.url_path, resouce_id)
        return self.do_http("DELETE", urlpath)

    # ==========================================================================
    def get_http(self, p_json=None):
        if p_json is None:
            p_json = {}
        return self.do_http('GET', self.url_path,
                            p_json=p_json, use_param_url=True)

    # ==========================================================================
    def post_http(self, p_json=None):
        if p_json is None:
            p_json = {}
        return self.do_http('POST', self.url_path, p_json=p_json)

    # ==========================================================================
    def put_http(self, p_json=None):
        if p_json is None:
            p_json = {}
        return self.do_http('PUT', self.url_path, p_json=p_json)

    # ==========================================================================
    def delete_http(self, p_json=None):
        if p_json is None:
            p_json = {}
        return self.do_http('DELETE', self.url_path, p_json=p_json)

    # ==========================================================================
    def do_http(self, method, urlpath, p_json=None, use_param_url=False):
        """
        DO HTTP base call
        :param method:
        :param urlpath:
        :param p_json:
        :param use_param_url:
        :return:
        """

        if p_json is None:
            p_json = {}
        _kwargs = {}
        if urlpath[0] == '/':
            urlpath = urlpath[1:]
        url = '%s/%s' % (self.url_base, urlpath)
        if use_param_url:
            url += "?json=%s" % requote_uri(json.dumps(p_json))
        else:
            _kwargs['json'] = p_json
        if self.use_https:
            _kwargs['verify'] = False
        if method.upper() == 'GET':
            response = self.session.get(url, **_kwargs)
        elif method.upper() == 'PUT':
            response = self.session.put(url, **_kwargs)
        elif method.upper() == 'POST':
            response = self.session.post(url, **_kwargs)
        elif method.upper() == 'DELETE':
            response = self.session.delete(url, **_kwargs)
        else:
            raise RuntimeError("Invalid HTTP method <%s>" % method.upper())
        r_json = convert_str(json.loads(response.text)) \
            if response.status_code == 200 else {}
        return response.status_code, r_json


################################################################################
class ApiClient(object):
    """ Restful Client simulation class """
    # ==========================================================================
    def __init__(self, url):
        self.url = url.lower()
        self.use_https = self.url.startswith('https:')
        self.session = requests.Session()

    # ==========================================================================
    def get(self, url_postfix, p_json=None):
        if p_json is None:
            p_json = {}
        return self.do_http('GET', url_postfix,
                            p_json=p_json, use_param_url=True)

    # ==========================================================================
    def post(self, url_postfix, p_json=None):
        if p_json is None:
            p_json = {}
        return self.do_http('POST', url_postfix, p_json=p_json)

    # ==========================================================================
    def put(self, url_postfix, p_json=None):
        if p_json is None:
            p_json = {}
        return self.do_http('PUT', url_postfix, p_json=p_json)

    # ==========================================================================
    def delete(self, url_postfix, p_json=None):
        if p_json is None:
            p_json = {}
        return self.do_http('DELETE', url_postfix, p_json=p_json)

    # ==========================================================================
    def do_http(self, method, url_postfix, p_json=None, use_param_url=False):
        if p_json is None:
            p_json = {}
        _kwargs = {}
        if url_postfix[0] == '/':
            url_postfix = url_postfix[1:]
        url = '%s/%s' % (self.url, url_postfix)
        if use_param_url:
            url += "?json=%s" % quote_plus(json.dumps(p_json))
        else:
            _kwargs['json'] = p_json
        if self.use_https:
            _kwargs['verify'] = False
        if method.upper() == 'GET':
            response = self.session.get(url, **_kwargs)
        elif method.upper() == 'PUT':
            response = self.session.put(url, **_kwargs)
        elif method.upper() == 'POST':
            response = self.session.post(url, **_kwargs)
        elif method.upper() == 'DELETE':
            response = self.session.delete(url, **_kwargs)
        else:
            raise RuntimeError("Invalid HTTP method <%s>" % method.upper())
        r_json = convert_str(json.loads(response.text)) \
            if response.status_code == 200 else {}
        return response.status_code, r_json
