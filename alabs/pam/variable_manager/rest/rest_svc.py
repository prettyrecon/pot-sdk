"""
====================================
 :mod:`alabs.common.rest.rest_svc` rest service using Flask-RESTful
====================================
.. moduleauthor:: 채문창 <mcchae@gmail.com>
.. note:: NDA License
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
# | /{rces}    | 새로운rce 등록 | rces목록리턴 | 여러rces bulk갱신|여러/모든 rces삭제|
# +------------+--------------|--------------+-----------------+---------------+
# |/{rces}/{id}|    에러   |{id}라는rce리턴 |{id} 라는 rce 갱신 |  {id} rce 삭제   |
# ==============================================================================
#
# The ok Method : URI : actions are
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
#  * [2019/02/19]
#     - alabs.common.rest 로 변경
################################################################################
import os
from flask import Flask
from flask_rextx import Api
from alabs.rest import ns_api, on_load

# from vivans.rest import MONGO_API_PREFIX, MONGO_API_NAME, MONGO_API_VERSION, \
#     MYSQL_API_PREFIX, MYSQL_API_NAME, MYSQL_API_VERSION, \
#     AAA_API_PREFIX, AAA_API_NAME, AAA_API_VERSION, \
#     PICKLE_API_PREFIX, PICKLE_API_NAME, PICKLE_API_VERSION, \
#     FILE_API_PREFIX, FILE_API_NAME, FILE_API_VERSION


################################################################################

# WITH_AAA = int(os.environ.get('WITH_AAA', '0'))
# if not WITH_AAA:
#     print('>>>NO AAA')
# else:
#     print('>>>WITH AAA')

################################################################################
app = None
try:
    # Flask app
    app = Flask(__name__)
    api = Api(
        title='CRUD-REST-Server',
        version='1.0',
        description='CRUD RESTful Server',
        # All API metadatas
    )
    on_load(app)
    api.add_namespace(ns_api, path='/%s/%s/%s'
                                   % (PICKLE_API_PREFIX, PICKLE_API_NAME,
                                      PICKLE_API_VERSION))
    app.logger.info("Start RestAPI from [%s]..." % __name__)
    api.init_app(app)
except Exception as err:
    if app and app.logger:
        app.logger.error('Error: %s' % str(err))
    raise

################################################################################
if __name__ == "__main__":
    api_port = os.environ.get('API_PORT')
    if not api_port:
        raise RuntimeError('API_PORT environment variable is not set!')
    app.run(host="0.0.0.0", port=int(api_port))
