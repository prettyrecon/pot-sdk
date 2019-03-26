#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod:`vivans.rest.rest_client` rest client using requests
====================================
.. moduleauthor:: 채문창 <mcchae@gmail.com>
.. note:: MIT License
"""

# 설명
# =====
#
# rest service using Flask-RESTful
#
# RESTAPI (http://bcho.tistory.com/914)
# ==============================================================================
# |   리소스     |     POST     |     GET     |     PUT      |     DELETE       |
# +------------+--------------|--------------+-----------------+----------------
# |            |    create    |     read    |     update    |      delete      |
# +------------+--------------|-------------+---------------+------------------+
# | /{rces}    | 새로운rce 등록 | rces목록리턴 | 여러rces bulk갱신|여러/모든 rces삭제 |
# +------------+--------------|--------------+-----------------+---------------+
# |/{rces}/{id}|    에러     |{id}라는rce리턴 |{id} 라는 rce 갱신| {id} rce 삭제   |
# ==============================================================================
#
# The success Method : URI : actions are
# ==============================================================================
# HTTP Method  |               URI               |          Action             |
# +------------+---------------------------------+-----------------------------|
#    GET       | http://{host}/api/v1.0/rces     | retrieve list of rces(필터등)|
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
#  * [2018/04/11]
#     - file 테스트 추가
#  * [2018/04/10]
#     - pickle 테스트 추가
#  * [2017/09/13]
#     - mysql 테스트 추가
#  * [2017/04/19]
#     - PEP8 맞춤
#  * [2017/04/13]
#     - 본 모듈 작업 시작

################################################################################
import os
import sys
import unittest
from alabs.rest import RestClient
from alabs import rest
from alabs.rest import get_passwd_hash

################################################################################
__author__ = "MoonChang Chae <mcchae@gmail.com>"
__date__ = "2017/04/19"
__version__ = "1.17.0419"
__version_info__ = (1, 17, 419)
__license__ = "MIT"


################################################################################
# noinspection PyMethodMayBeStatic,PyUnresolvedReferences
class TU (unittest.TestCase):
    # ==========================================================================
    isFirst = True

    # ==========================================================================
    def myInit(self):
        if TU.isFirst:
            TU.isFirst = False
            TU.API_HOST = os.environ.get('API_HOST')
            if not TU.API_HOST:
                raise RuntimeError(
                    'API_HOST environment variable is not set!')
            TU.API_PORT = os.environ.get('API_PORT')
            if not TU.API_PORT:
                raise RuntimeError(
                    'API_PORT environment variable is not set!')
            TU.WITH_AAA = int(os.environ.get('WITH_AAA', '0'))
            if not TU.WITH_AAA:
                print('>>>NO AAA')
            else:
                print('>>>WITH AAA')
            TU.rc_api = RestClient(TU.API_HOST, TU.API_PORT, 'foos',
                                   url_prefix=rest.MONGO_API_PREFIX,
                                   api_name=rest.MONGO_API_NAME,
                                   api_version=rest.MONGO_API_VERSION)

    # ==========================================================================
    def setUp(self):
        self.myInit()

    # ==========================================================================
    def tearDown(self):
        pass

    # ==========================================================================
    def test0000_init(self):
        self.assertTrue(True)

    # ==========================================================================
    def test0005_ping_api_all(self):
        # mongo api blueprint ping
        TU.rc_api.set_api_url('mongo', 'ping')
        rc, rj = TU.rc_api.get_http()
        self.assertTrue(rc == 200 and rj['success'])
        # pickle api blueprint ping
        TU.rc_api.set_api_url('pickle', 'ping')
        rc, rj = TU.rc_api.get_http()
        self.assertTrue(rc == 200 and rj['success'])
        # file api blueprint ping
        TU.rc_api.set_api_url('file', 'ping')
        rc, rj = TU.rc_api.get_http()
        self.assertTrue(rc == 200 and rj['success'])
        # mysql api blueprint ping
        TU.rc_api.set_api_url('mysql', 'ping')
        rc, rj = TU.rc_api.get_http()
        self.assertTrue(rc == 200 and rj['success'])
        # aaa api blueprint ping
        TU.rc_api.set_api_url('aaa', 'ping')
        rc, rj = TU.rc_api.get_http()
        self.assertTrue(rc == 200 and rj['success'])

    # ==========================================================================
    def test0010_get_all(self):
        TU.rc_api.set_api_url('mongo')
        rc, rj = TU.rc_api.get_all()
        self.assertTrue(rc == 401 if TU.WITH_AAA else 200)  # unauthorized Error

    # ==========================================================================
    def test0015_login_fail(self):
        if not TU.WITH_AAA:
            return
        TU.rc_api.set_api_url('aaa', 'login')
        p_json = {
            'user_id': 'admin',
            'password': get_passwd_hash('admin_000'),  # login fail test
        }
        rc, rj = TU.rc_api.post_http(p_json)
        self.assertTrue(rc == 200 and not rj['success'])

    # ==========================================================================
    def test0018_execute_sql(self):
        if not TU.WITH_AAA:
            return
        TU.rc_api.set_api_url('mysql', 'execute_sql')
        p_json = {
            'sql': 'SELECT 1 as ping'
        }
        rc, rj = TU.rc_api.post_http(p_json)
        self.assertTrue(rc == 401 if TU.WITH_AAA else 200)  # unauthorized Error

    # ==========================================================================
    def test0020_get_all(self):
        TU.rc_api.set_api_url('mongo')
        if not TU.WITH_AAA:
            return
        rc, rj = TU.rc_api.get_all()
        self.assertTrue(rc == 401 if TU.WITH_AAA else 200)  # unauthorized Error

    # ==========================================================================
    def test0022_get_all(self):
        TU.rc_api.set_api_url('mysql')
        if not TU.WITH_AAA:
            return
        rc, rj = TU.rc_api.get_all()
        self.assertTrue(rc == 401 if TU.WITH_AAA else 200)  # unauthorized Error

    # ==========================================================================
    def test0025_login_success(self):
        if not TU.WITH_AAA:
            return
        TU.rc_api.set_api_url('aaa', 'login')
        p_json = {
            'user_id': 'admin',
            'password': get_passwd_hash('admin_pass'),  # login success test
        }
        rc, rj = TU.rc_api.post_http(p_json)
        self.assertTrue(rc == 200 and rj['success'])

    # ==========================================================================
    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
    def test0050_execute_sql(self):
        if not TU.WITH_AAA:
            return
        TU.rc_api.set_api_url('mysql', 'execute_sql')
        p_json = {
            'sql': '''CREATE TABLE IF NOT EXISTS foos (
    id bigint not null auto_increment,
    name varchar(50),
    age int default 0,
    sex varchar(10),
    kind varchar(20),
    children tinyint default 0,
    primary key (id)
)'''
        }
        rc, rj = TU.rc_api.post_http(p_json)
        self.assertTrue(rc == 200 and rj['success'])  # unauthorized Error

    # ==========================================================================
    def test0120_get_all(self):
        TU.rc_api.set_api_url('mongo')
        rc, rj = TU.rc_api.get_all()
        self.assertTrue(rc == 200 and rj['success'])
        if rj['data']:
            rc, rj = TU.rc_api.delete_all()
            self.assertTrue(rc == 200 and rj['success'])

    # ==========================================================================
    def test0122_get_all(self):
        TU.rc_api.set_api_url('mysql')
        rc, rj = TU.rc_api.get_all()
        self.assertTrue(rc == 200 and rj['success'])
        if rj['data']:
            rc, rj = TU.rc_api.delete_all()
            self.assertTrue(rc == 200 and rj['success'])

    # ==========================================================================
    def test0124_get_all(self):
        TU.rc_api.set_api_url('pickle')
        rc, rj = TU.rc_api.get_all()
        self.assertTrue(rc == 200 and rj['success'])
        if rj['data']:
            rc, rj = TU.rc_api.delete_all()
            self.assertTrue(rc == 200 and rj['success'])

    # ==========================================================================
    def test0126_get_all(self):
        TU.rc_api.set_api_url('file')
        rc, rj = TU.rc_api.get_all()
        self.assertTrue(rc == 200 and rj['success'])
        if rj['data']:
            rc, rj = TU.rc_api.delete_all()
            self.assertTrue(rc == 200 and rj['success'])

    # ==========================================================================
    def test0140_grant_clear(self):
        TU.rc_api.set_api_url('aaa', 'grant_clear')
        rc, rj = TU.rc_api.get_http()
        self.assertTrue(rc == 200 and rj['success'])
        TU.rc_api.set_api_url('aaa', 'grant_get')
        rc, rj = TU.rc_api.get_http()
        self.assertTrue(rc == 200 and rj['success'])
        print(rj['result'])

    # ==========================================================================
    def test0150_index_information(self):
        TU.rc_api.set_api_url('mongo', 'index_information')
        rc, rj = TU.rc_api.post_http({'collection': 'foos'})
        self.assertTrue(rc == 200 and rj['success'])
        if isinstance(rj['result'], dict) and rj['result']:
            for k in rj['result'].keys():
                TU.rc_api.set_api_url('mongo', 'drop_index')
                rc, rj = TU.rc_api.post_http({'collection': 'foos', 'index': k})
                self.assertTrue(rc == 200 and rj['success'])

        TU.rc_api.set_api_url('mongo', 'index_information')
        rc, rj = TU.rc_api.post_http({'collection': 'foos'})
        self.assertTrue(rc == 200 and rj['success'] and not rj['result'])

    # ==========================================================================
    def test0160_create_index(self):
        TU.rc_api.set_api_url('mongo', 'create_index')
        p_json = {
            'collection': 'foos',
            # 'name' 속성은 오름차순 'age' 속성은 내림차순으로 색인 요청
            'index': [('name', 1), ('age', -1)],
        }
        rc, rj = TU.rc_api.post_http(p_json)
        self.assertTrue(rc == 200 and rj['success'] and rj['result'])
        print(rj['result'])

    # ==========================================================================
    def test0170_index_information(self):
        TU.rc_api.set_api_url('mongo', 'index_information')
        rc, rj = TU.rc_api.post_http({'collection': 'foos'})
        self.assertTrue(rc == 200 and rj['success'] and rj['result'])
        print(rj['result'])

    # ==========================================================================
    def test0180_create(self):
        TU.rc_api.set_api_url('mongo')
        a_data = {"name": "행운이", "age": 3, "sex": "여", "kind": "puddle",
                  'metadata': {'name': 'mt01', 'version':'1.0'}}
        rc, rj = TU.rc_api.create(a_data)
        TU.mongo_uid1 = rj['data'][0]['_uid']
        self.assertTrue(rc == 200 and rj['success'])
        a_data = {"name": "복실이", "age": 13, "sex": "남", "kind": "mix",
                  'metadata': {'name': 'mt02', 'version': '1.1'}}
        rc, rj = TU.rc_api.create(a_data)
        TU.mongo_uid2 = rj['data'][0]['_uid']
        self.assertTrue(rc == 200 and rj['success'])

    # ==========================================================================
    def test0182_create(self):
        TU.rc_api.set_api_url('mysql')
        a_data = {"name": "행운이", "age": 3, "sex": "여", "kind": "puddle"}
        rc, rj = TU.rc_api.create(a_data)
        self.assertTrue(rc == 200 and rj['success'])
        TU.mysql_uid1 = rj['data'][0]['_uid']
        a_data = {"name": "복실이", "age": 13, "sex": "남", "kind": "mix"}
        rc, rj = TU.rc_api.create(a_data)
        self.assertTrue(rc == 200 and rj['success'])
        TU.mysql_uid2 = rj['data'][0]['_uid']

    # ==========================================================================
    def test0184_create(self):
        TU.rc_api.set_api_url('pickle')
        a_data = {"name": "행운이", "age": 3, "sex": "여", "kind": "puddle",
                  'metadata': {'name': 'mt01', 'version':'1.0'}}
        rc, rj = TU.rc_api.create(a_data)
        TU.pickle_uid1 = rj['data'][0]['_uid']
        self.assertTrue(rc == 200 and rj['success'])
        a_data = {"name": "복실이", "age": 13, "sex": "남", "kind": "mix",
                  'metadata': {'name': 'mt02', 'version': '1.1'}}
        rc, rj = TU.rc_api.create(a_data)
        TU.pickle_uid2 = rj['data'][0]['_uid']
        self.assertTrue(rc == 200 and rj['success'])

    # ==========================================================================
    def test0186_create(self):
        TU.rc_api.set_api_url('file')
        a_data = {"name": "행운이", "age": 3, "sex": "여", "kind": "puddle",
                  'metadata': {'name': 'mt01', 'version':'1.0'}}
        rc, rj = TU.rc_api.create(a_data)
        TU.file_uid1 = rj['data'][0]['_uid']
        self.assertTrue(rc == 200 and rj['success'])
        a_data = {"name": "복실이", "age": 13, "sex": "남", "kind": "mix",
                  'metadata': {'name': 'mt02', 'version': '1.1'}}
        rc, rj = TU.rc_api.create(a_data)
        TU.file_uid2 = rj['data'][0]['_uid']
        self.assertTrue(rc == 200 and rj['success'])

    # ==========================================================================
    def test0200_get(self):
        TU.rc_api.set_api_url('mongo')
        rc, rj = TU.rc_api.get(TU.mongo_uid2)
        self.assertTrue(rc == 200 and rj['success'] and
                        rj['data']['name'] == '복실이')
        rc, rj = TU.rc_api.get(100)
        self.assertTrue(rc == 200 and not (rj['success'] or rj['data']))

    # ==========================================================================
    def test0202_get(self):
        TU.rc_api.set_api_url('mysql')
        rc, rj = TU.rc_api.get(TU.mysql_uid2)
        self.assertTrue(rc == 200 and rj['success'] and
                        rj['data']['name'] == '복실이')
        rc, rj = TU.rc_api.get(100)
        self.assertTrue(rc == 200 and not (rj['success'] or rj['data']))

    # ==========================================================================
    def test0204_get(self):
        TU.rc_api.set_api_url('pickle')
        rc, rj = TU.rc_api.get(TU.pickle_uid2)
        self.assertTrue(rc == 200 and rj['success'] and
                        rj['data']['name'] == '복실이')
        rc, rj = TU.rc_api.get(100)
        self.assertTrue(rc == 200 and not (rj['success'] or rj['data']))

    # ==========================================================================
    def test0206_get(self):
        TU.rc_api.set_api_url('file')
        rc, rj = TU.rc_api.get(TU.file_uid2)
        self.assertTrue(rc == 200 and rj['success'] and
                        rj['data']['name'] == '복실이')
        rc, rj = TU.rc_api.get(100)
        self.assertTrue(rc == 200 and not (rj['success'] or rj['data']))

    # ==========================================================================
    def test0300_update(self):
        TU.rc_api.set_api_url('mongo')
        a_data = {"age": 30, "kind": "grand_puddle", "children": 10}
        rc, rj = TU.rc_api.update(TU.mongo_uid1, a_data)
        self.assertTrue(rc == 200 and rj['success'] and rj['data'])
        rc, rj = TU.rc_api.get(TU.mongo_uid1)
        self.assertTrue(rc == 200 and rj['success'] and
                        rj['data']['name'] == '행운이' and
                        rj['data']['children'] == 10)
        rc, rj = TU.rc_api.update(2000, a_data)
        self.assertTrue(rc == 200 and not (rj['success'] or rj['data']))

    # ==========================================================================
    def test0302_update(self):
        TU.rc_api.set_api_url('mysql')
        a_data = {"age": 30, "kind": "grand_puddle", "children": 10}
        rc, rj = TU.rc_api.update(TU.mysql_uid1, a_data)
        self.assertTrue(rc == 200 and rj['success'] and rj['data'])
        rc, rj = TU.rc_api.get(TU.mysql_uid1)
        self.assertTrue(rc == 200 and rj['success'] and
                        rj['data']['name'] == '행운이' and
                        rj['data']['children'] == 10)
        rc, rj = TU.rc_api.update(2000, a_data)
        self.assertTrue(rc == 200 and not (rj['success'] or rj['data']))

    # ==========================================================================
    def test0304_update(self):
        TU.rc_api.set_api_url('pickle')
        a_data = {"age": 30, "kind": "grand_puddle", "children": 10}
        rc, rj = TU.rc_api.update(TU.pickle_uid1, a_data)
        self.assertTrue(rc == 200 and rj['success'] and rj['data'])
        rc, rj = TU.rc_api.get(TU.pickle_uid1)
        self.assertTrue(rc == 200 and rj['success'] and
                        rj['data']['name'] == '행운이' and
                        rj['data']['children'] == 10)
        rc, rj = TU.rc_api.update(2000, a_data)
        self.assertTrue(rc == 200 and not (rj['success'] or rj['data']))

    # ==========================================================================
    def test0306_update(self):
        TU.rc_api.set_api_url('file')
        a_data = {"age": 30, "kind": "grand_puddle", "children": 10}
        rc, rj = TU.rc_api.update(TU.file_uid1, a_data)
        self.assertTrue(rc == 200 and rj['success'] and rj['data'])
        rc, rj = TU.rc_api.get(TU.file_uid1)
        self.assertTrue(rc == 200 and rj['success'] and
                        rj['data']['name'] == '행운이' and
                        rj['data']['children'] == 10)
        rc, rj = TU.rc_api.update(2000, a_data)
        self.assertTrue(rc == 200 and not (rj['success'] or rj['data']))

    # ==========================================================================
    def test0330_get_all(self):
        TU.rc_api.set_api_url('mongo')
        rc, rj = TU.rc_api.get_all()
        for row in rj['data']:
            print(row['name'])
        self.assertTrue(rc == 200 and len(rj['data']) == 2)
        find_kwargs = {'filter': {'name': u'복실이'}}
        rc, rj = TU.rc_api.get_all(find_kwargs)
        for row in rj['data']:
            print(row['name'])
        self.assertTrue(rc == 200 and rj['success'] and len(rj['data']) == 1)
        find_kwargs = {'filter': {'metadata.name': 'mt01'}}
        rc, rj = TU.rc_api.get_all(find_kwargs)
        for row in rj['data']:
            print('test0330_get_all:(%s:%s)'
                  % (row['name'], row['metadata']['name']))
        self.assertTrue(rc == 200 and rj['success'] and len(rj['data']) == 1)
        # 이제 특정 키를 찾는데 k1.k2::=keyval 과 같은 형식으로 가능
        rc, rj = TU.rc_api.get("metadata.name::=mt02")
        self.assertTrue(rc == 200 and rj['success'] and
                        rj['data']['name'] == '복실이' and
                        rj['data']['metadata']['name'] == 'mt02')

    # ==========================================================================
    def test0332_get_all(self):
        TU.rc_api.set_api_url('mysql')
        rc, rj = TU.rc_api.get_all()
        for row in rj['data']:
            print(row['name'])
        self.assertTrue(rc == 200 and len(rj['data']) == 2)
        find_kwargs = {'filter': {'name': u'복실이'}}
        rc, rj = TU.rc_api.get_all(find_kwargs)
        for row in rj['data']:
            print(row['name'])
        self.assertTrue(rc == 200 and rj['success'] and len(rj['data']) == 1)

    # ==========================================================================
    def test0334_get_all(self):
        TU.rc_api.set_api_url('pickle')
        rc, rj = TU.rc_api.get_all()
        for row in rj['data']:
            print(row['name'])
        self.assertTrue(rc == 200 and len(rj['data']) == 2)
        find_kwargs = {'filter': {'name': u'복실이'}}
        rc, rj = TU.rc_api.get_all(find_kwargs)
        for row in rj['data']:
            print(row['name'])
        self.assertTrue(rc == 200 and rj['success'] and len(rj['data']) == 1)
        find_kwargs = {'filter': {'metadata.name': 'mt01'}}
        rc, rj = TU.rc_api.get_all(find_kwargs)
        for row in rj['data']:
            print('test0334_get_all:(%s:%s)'
                  % (row['name'], row['metadata']['name']))
        self.assertTrue(rc == 200 and rj['success'] and len(rj['data']) == 1)
        # 이제 특정 키를 찾는데 k1.k2::=keyval 과 같은 형식으로 가능
        rc, rj = TU.rc_api.get("metadata.name::=mt02")
        self.assertTrue(rc == 200 and rj['success'] and
                        rj['data']['name'] == '복실이' and
                        rj['data']['metadata']['name'] == 'mt02')

    # ==========================================================================
    def test0336_get_all(self):
        TU.rc_api.set_api_url('file')
        rc, rj = TU.rc_api.get_all()
        for row in rj['data']:
            print(row['name'])
        self.assertTrue(rc == 200 and len(rj['data']) == 2)
        find_kwargs = {'filter': {'name': u'복실이'}}
        rc, rj = TU.rc_api.get_all(find_kwargs)
        for row in rj['data']:
            print(row['name'])
        self.assertTrue(rc == 200 and rj['success'] and len(rj['data']) == 1)
        find_kwargs = {'filter': {'metadata.name': 'mt01'}}
        rc, rj = TU.rc_api.get_all(find_kwargs)
        for row in rj['data']:
            print('test0336_get_all:(%s:%s)'
                  % (row['name'], row['metadata']['name']))
        self.assertTrue(rc == 200 and rj['success'] and len(rj['data']) == 1)
        # 이제 특정 키를 찾는데 k1.k2::=keyval 과 같은 형식으로 가능
        rc, rj = TU.rc_api.get("metadata.name::=mt02")
        self.assertTrue(rc == 200 and rj['success'] and
                        rj['data']['name'] == '복실이' and
                        rj['data']['metadata']['name'] == 'mt02')

    # ==========================================================================
    def test0350_delete(self):
        TU.rc_api.set_api_url('mongo')
        rc, rj = TU.rc_api.delete(TU.mongo_uid2)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['deleted_count'] == 1)
        rc, rj = TU.rc_api.delete(1000)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['deleted_count'] == 0)
        rc, rj = TU.rc_api.get_all()
        self.assertTrue(rc == 200 and rj['success'] and len(rj['data']) == 1)

    # ==========================================================================
    def test0352_delete(self):
        TU.rc_api.set_api_url('mysql')
        rc, rj = TU.rc_api.delete(TU.mysql_uid2)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['deleted_count'] == 1)
        rc, rj = TU.rc_api.delete(1000)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['deleted_count'] == 0)
        rc, rj = TU.rc_api.get_all()
        self.assertTrue(rc == 200 and rj['success'] and len(rj['data']) == 1)

    # ==========================================================================
    def test0354_delete(self):
        TU.rc_api.set_api_url('pickle')
        rc, rj = TU.rc_api.delete(TU.pickle_uid2)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['deleted_count'] == 1)
        rc, rj = TU.rc_api.delete(1000)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['deleted_count'] == 0)
        rc, rj = TU.rc_api.get_all()
        self.assertTrue(rc == 200 and rj['success'] and len(rj['data']) == 1)

    # ==========================================================================
    def test0356_delete(self):
        TU.rc_api.set_api_url('file')
        rc, rj = TU.rc_api.delete(TU.file_uid2)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['deleted_count'] == 1)
        rc, rj = TU.rc_api.delete(1000)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['deleted_count'] == 0)
        rc, rj = TU.rc_api.get_all()
        self.assertTrue(rc == 200 and rj['success'] and len(rj['data']) == 1)

    # ==========================================================================
    def test0380_create_some(self):
        TU.rc_api.set_api_url('mongo')
        for i in range(10):
            a_data = {"name": "개%d" % i, "age": i+100,
                      "sex": "여", "kind": "all"}
            rc, rj = TU.rc_api.create(a_data)
            self.assertTrue(rc == 200 and rj['success'])
        rc, rj = TU.rc_api.get_all()
        self.assertTrue(rc == 200 and rj['success'] and len(rj['data']) == 11)

    # ==========================================================================
    def test0382_create_some(self):
        TU.rc_api.set_api_url('mysql')
        for i in range(10):
            a_data = {"name": "개%d" % i, "age": i+100,
                      "sex": "여", "kind": "all"}
            rc, rj = TU.rc_api.create(a_data)
            self.assertTrue(rc == 200 and rj['success'])
        rc, rj = TU.rc_api.get_all()
        self.assertTrue(rc == 200 and rj['success'] and len(rj['data']) == 11)

    # ==========================================================================
    def test0384_create_some(self):
        TU.rc_api.set_api_url('pickle')
        for i in range(10):
            a_data = {"name": "개%d" % i, "age": i+100,
                      "sex": "여", "kind": "all"}
            rc, rj = TU.rc_api.create(a_data)
            self.assertTrue(rc == 200 and rj['success'])
        rc, rj = TU.rc_api.get_all()
        self.assertTrue(rc == 200 and rj['success'] and len(rj['data']) == 11)

    # ==========================================================================
    def test0386_create_some(self):
        TU.rc_api.set_api_url('file')
        for i in range(10):
            a_data = {"name": "개%d" % i, "age": i+100,
                      "sex": "여", "kind": "all"}
            rc, rj = TU.rc_api.create(a_data)
            self.assertTrue(rc == 200 and rj['success'])
        rc, rj = TU.rc_api.get_all()
        self.assertTrue(rc == 200 and rj['success'] and len(rj['data']) == 11)

    # ==========================================================================
    def test0400_select_filter(self):
        TU.rc_api.set_api_url('mongo')
        where = {
            'filter': {'age': {'$gte': 100}},
            'skip': 2,
            'limit': 4,
            'sort': [('age', -1)],    # 'age'로 내림차순 정렬
        }
        rc, rj = TU.rc_api.get_all(where)
        self.assertTrue(rc == 200 and rj['success'] and len(rj['data']) == 4
                        and rj['data'][3]['age'] == 104
                        and rj['total_count'] == 10)

    # ==========================================================================
    def test0402_select_filter(self):
        TU.rc_api.set_api_url('mysql')
        #
        where = {
            'where': 'age >= 100 ORDER BY age DESC LIMIT 2, 4'
        }
        rc, rj = TU.rc_api.get_all(where)
        self.assertTrue(rc == 200 and len(rj['data']) == 4
                        and rj['data'][3]['age'] == 104)
        where = {
            'filter': {'age': {'$gte': 100}},
            'skip': 2,
            'limit': 4,
            'sort': [('age', -1)],    # 'age'로 내림차순 정렬
        }
        rc, rj = TU.rc_api.get_all(where)
        self.assertTrue(rc == 200 and rj['success'] and len(rj['data']) == 4
                        and rj['data'][3]['age'] == 104
                        and rj['total_count'] == 10)

    # ==========================================================================
    def test0404_select_filter(self):
        TU.rc_api.set_api_url('pickle')
        where = {
            'filter': {'age': {'$gte': 100}},
            'skip': 2,
            'limit': 4,
            'sort': [('age', -1)],    # 'age'로 내림차순 정렬
        }
        rc, rj = TU.rc_api.get_all(where)
        self.assertTrue(rc == 200 and rj['success'] and len(rj['data']) == 4
                        and rj['data'][3]['age'] == 104
                        and rj['total_count'] == 10)

    # ==========================================================================
    def test0406_select_filter(self):
        TU.rc_api.set_api_url('file')
        where = {
            'filter': {'age': {'$gte': 100}},
            'skip': 2,
            'limit': 4,
            'sort': [('age', -1)],    # 'age'로 내림차순 정렬
        }
        # todo: sort 는 아직 적용 안되었음
        rc, rj = TU.rc_api.get_all(where)
        self.assertTrue(rc == 200 and rj['success'] and len(rj['data']) == 4
                        # and rj['data'][3]['age'] == 104
                        and rj['total_count'] == 10)

    # ==========================================================================
    def test0460_delete_some(self):
        TU.rc_api.set_api_url('mongo')
        find_kwargs = {'filter': {'age': {'$gte': 105}}}
        rc, rj = TU.rc_api.delete_all(find_kwargs)
        print(rj)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['deleted_count'] == 5)

    # ==========================================================================
    def test0462_delete_some(self):
        TU.rc_api.set_api_url('mysql')
        find_kwargs = {'filter': {'age': {'$gte': 105}}}
        rc, rj = TU.rc_api.delete_all(find_kwargs)
        print(rj)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['deleted_count'] == 5)

    # ==========================================================================
    def test0464_delete_some(self):
        TU.rc_api.set_api_url('pickle')
        find_kwargs = {'filter': {'age': {'$gte': 105}}}
        rc, rj = TU.rc_api.delete_all(find_kwargs)
        print(rj)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['deleted_count'] == 5)

    # ==========================================================================
    def test0466_delete_some(self):
        TU.rc_api.set_api_url('file')
        find_kwargs = {'filter': {'age': {'$gte': 105}}}
        rc, rj = TU.rc_api.delete_all(find_kwargs)
        print(rj)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['deleted_count'] == 5)

    # ==========================================================================
    def test0480_update_some(self):
        TU.rc_api.set_api_url('mongo')
        _sets = {"sex": "남", "kind": "mod"}
        _filter = {'age': {'$gte': 101}}
        rc, rj = TU.rc_api.update_all(_sets, _filter)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['updated_count'] == 4)

        _sets = {"sex": "전", "kind": "updated"}
        rc, rj = TU.rc_api.update_all(_sets)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['updated_count'] == 6)

    # ==========================================================================
    def test0482_update_some(self):
        TU.rc_api.set_api_url('mysql')
        _sets = {"sex": "남", "kind": "mod"}
        _filter = {'age': {'$gte': 101}}
        rc, rj = TU.rc_api.update_all(_sets, _filter)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['updated_count'] == 4)

        _sets = {"sex": "전", "kind": "updated"}
        rc, rj = TU.rc_api.update_all(_sets)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['updated_count'] == 6)

    # ==========================================================================
    def test0484_update_some(self):
        TU.rc_api.set_api_url('pickle')
        _sets = {"sex": "남", "kind": "mod"}
        _filter = {'age': {'$gte': 101}}
        rc, rj = TU.rc_api.update_all(_sets, _filter)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['updated_count'] == 4)

        _sets = {"sex": "전", "kind": "updated"}
        rc, rj = TU.rc_api.update_all(_sets)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['updated_count'] == 6)

    # ==========================================================================
    def test0486_update_some(self):
        TU.rc_api.set_api_url('file')
        _sets = {"sex": "남", "kind": "mod"}
        _filter = {'age': {'$gte': 101}}
        rc, rj = TU.rc_api.update_all(_sets, _filter)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['updated_count'] == 4)

        _sets = {"sex": "전", "kind": "updated"}
        rc, rj = TU.rc_api.update_all(_sets)
        self.assertTrue(rc == 200 and rj['success']
                        and rj['updated_count'] == 6)

    # ==========================================================================
    def test0600_append_audit_log(self):
        TU.rc_api.set_api_url('mysql', 'append_audit_log')
        audit_log = {
            'where': "WHERE 여기 요기 조기",
            'desc': "주저리 주저리",
            'status': "테스트",
            'elapsed': 0.1234,
        }
        rc, rj = TU.rc_api.post_http(audit_log)
        self.assertTrue(rc == 200 and rj['success'])

    # ==========================================================================
    def test0700_mongo_id_attr(self):
        # 기존의 색인을 재생성하기 위하여 기존 색인 모두 삭제
        TU.rc_api.set_api_url('mongo', 'index_information')
        rc, rj = TU.rc_api.post_http({'collection': 'foos'})
        self.assertTrue(rc == 200 and rj['success'])
        if isinstance(rj['result'], dict) and rj['result']:
            for k in rj['result'].keys():
                TU.rc_api.set_api_url('mongo', 'drop_index')
                rc, rj = TU.rc_api.post_http({'collection': 'foos', 'index': k})
                self.assertTrue(rc == 200 and rj['success'])
        # 사용자 정의 고유키를 이용하기 위하여 default 'foos' 컬랙션 모두 삭제
        TU.rc_api.set_api_url('mongo')
        rc, rj = TU.rc_api.delete_all()
        self.assertTrue(rc == 200 and rj['success'])
        # 'myid' 라는 이름의 고유키 생성
        TU.rc_api.set_api_url('mongo', 'create_index')
        p_json = {
            'collection': 'foos',
            'index': [('myid', 1)],
            'unique': True,
        }
        rc, rj = TU.rc_api.post_http(p_json)
        self.assertTrue(rc == 200 and rj['success'] and rj['result'])
        TU.rc_api.set_api_url('mongo')
        # 테스트로 10개를 넣음; 'myid'를 위에서 지정한 키로 인식
        for i in range(10):
            a_data = {
                "myid": "key_%s" % i,
                "name": "개%s" % (i+200),
                "age": i+200,
                "sex": "여",
                "kind": "all"
            }
            rc, rj = TU.rc_api.create(a_data)
            self.assertTrue(rc == 200 and rj['success'])
        rc, rj = TU.rc_api.get_all()
        self.assertTrue(rc == 200 and len(rj['data']) == 10)
        # 중복키를 넣으려 하면 duplecate key error 발생 확인
        a_data = {
            "myid": "key_%s" % 3,
            "name": "개%s" % (3 + 200),
            "age": 3 + 200,
            "sex": "여",
            "kind": "all"
        }
        rc, rj = TU.rc_api.create(a_data)
        self.assertTrue(not(rc == 200 and rj['success']))
        # 이제 특정 키를 찾는데 keyname::=keyval 과 같은 형식으로 넣으면 해당 keyname을 찾음
        rc, rj = TU.rc_api.get("%s::=key_%s" % ('myid', 3))
        self.assertTrue(rc == 200 and rj['success'] and
                        rj['data']['name'] == '개203' and
                        rj['data']['age'] == 203)

    # ==========================================================================
    def test0800_grant_add(self):
        TU.rc_api.set_api_url('aaa', 'grant_add')
        p_json = {
            'users': {
                'api_rest': ['read', 'write', 'create', 'delete'],
                'page_root': ['read'],
                'page_user': ['read', 'write', 'create', 'delete'],
                'page_guest': ['read', 'write', 'create', 'delete'],
            },
            'guests': {
                'page_user': ['read'],
                'page_guest': ['read', 'write', 'create', 'delete'],
            }
        }
        rc, rj = TU.rc_api.post_http(p_json)
        self.assertTrue(rc == 200 and rj['success'])

    # ==========================================================================
    def test0810_grant_get(self):
        TU.rc_api.set_api_url('aaa', 'grant_get')
        rc, rj = TU.rc_api.get_http()
        self.assertTrue(rc == 200 and rj['success'])
        print(rj['result'])

    # ==========================================================================
    def test0820_add_test_users(self):
        TU.rc_api.set_api_url('mongo', 'users')
        a_data = {'user_id': '_test_user1',
                  'password': get_passwd_hash('user1_pass'),
                  'roles': ['users']}
        rc, rj = TU.rc_api.create(a_data)
        self.assertTrue(rc == 200 and rj['success'])
        a_data = {'user_id': '_test_guest1',
                  'password': get_passwd_hash('guest1_pass'),
                  'roles': ['guest']}
        rc, rj = TU.rc_api.create(a_data)
        self.assertTrue(rc == 200 and rj['success'])

    # ==========================================================================
    def test0830_get_audits(self):
        TU.rc_api.set_api_url('mysql', 'audits')
        rc, rj = TU.rc_api.get_all()
        self.assertTrue(rc == 200 and len(rj['data']) == 100)

    # ==========================================================================
    def test0840_logout(self):
        if not TU.WITH_AAA:
            return
        TU.rc_api.set_api_url('aaa', 'logout')
        rc, rj = TU.rc_api.post_http()
        self.assertTrue(rc == 200 and rj['success'])

    # ==========================================================================
    def test0900_login_success(self):
        if not TU.WITH_AAA:
            return
        TU.rc_api.set_api_url('aaa', 'login')
        p_json = {
            'user_id': '_test_user1',
            'password': get_passwd_hash('user1_pass'),  # login success test
        }
        rc, rj = TU.rc_api.post_http(p_json)
        self.assertTrue(rc == 200 and rj['success'])

    # ==========================================================================
    def test0910_grant_clear_authorization_failure(self):
        TU.rc_api.set_api_url('aaa', 'grant_clear')
        rc, rj = TU.rc_api.get_http()
        self.assertTrue(rc == 200 and not rj['success'])

    # ==========================================================================
    def test0920_grant_check_success(self):
        TU.rc_api.set_api_url('aaa', 'grant_check')
        a_data = {
            'resource': 'page_root',
            'permission': 'read'
        }
        rc, rj = TU.rc_api.post_http(a_data)
        self.assertTrue(rc == 200 and rj['success'])

    # ==========================================================================
    def test0930_grant_check_failure(self):
        TU.rc_api.set_api_url('aaa', 'grant_check')
        a_data = {
            'resource': 'page_root',
            'permission': 'write'
        }
        rc, rj = TU.rc_api.post_http(a_data)
        self.assertTrue(rc == 200 and not rj['success'])

    # ==========================================================================
    def test9900_logout(self):
        if not TU.WITH_AAA:
            return
        TU.rc_api.set_api_url('aaa', 'logout')
        rc, rj = TU.rc_api.post_http()
        self.assertTrue(rc == 200 and rj['success'])

    # ==========================================================================
    def test9910_get_all_unauthorized(self):
        TU.rc_api.set_api_url('mongo')
        rc, rj = TU.rc_api.get_all()
        self.assertTrue(rc == 401 if TU.WITH_AAA else 200)  # unauthorized Error

    # ==========================================================================
    def test9970_login_success(self):
        if not TU.WITH_AAA:
            return
        TU.rc_api.set_api_url('aaa', 'login')
        p_json = {
            'user_id': 'admin',
            'password': get_passwd_hash('admin_pass'),  # login success test
        }
        rc, rj = TU.rc_api.post_http(p_json)
        self.assertTrue(rc == 200 and rj['success'])

    # ==========================================================================
    def test9980_clear_test_users(self):
        TU.rc_api.set_api_url('mongo', 'users')
        rc, rj = TU.rc_api.delete('user_id::=_test_user1')
        self.assertTrue(rc == 200 and rj['success'])
        rc, rj = TU.rc_api.delete('user_id::=_test_guest1')
        self.assertTrue(rc == 200 and rj['success'])

    # ==========================================================================
    def test9990_logout(self):
        if not TU.WITH_AAA:
            return
        TU.rc_api.set_api_url('aaa', 'logout')
        rc, rj = TU.rc_api.post_http()
        self.assertTrue(rc == 200 and rj['success'])


################################################################################
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TU)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    ret = not result.wasSuccessful()
    sys.exit(ret)
