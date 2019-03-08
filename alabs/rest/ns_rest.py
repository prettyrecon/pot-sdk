"""
====================================
 :mod:`alabs.common.rest.ns_rest` rest service using Flask-RESTful template
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
# | /{rces}    | 새로운rce 등록 | rces목록리턴 |여러rces bulk갱신|여러/모든 rces 삭제|
# +------------+--------------|--------------+-----------------+---------------+
# |/{rces}/{id}|    에러      |{id}라는rce리턴 |{id} 라는 rce 갱신| {id} rce 삭제  |
# ==============================================================================
#
# The ok Method : URI : actions are
# ==============================================================================
# HTTP Method  |               URI               |          Action             |
# +------------+---------------------------------+-----------------------------|
#    GET       | http://{host}/ns_api/v1.0/rces     | retrieve list of rces(필터등)|
#    POST      | http://{host}/ns_api/v1.0/rces     | create a new rce            |
#    DELETE    | http://{host}/ns_api/v1.0/rces     | delete all rces (필터)       |
# +------------+---------------------------------+-----------------------------|
#    GET       | http://{host}/ns_api/v1.0/rces/{id}| retrieve a rce              |
#    PUT       | http://{host}/ns_api/v1.0/rces/{id}| update a rce                |
#    DELETE    | http://{host}/ns_api/v1.0/rces/{id}| delete a rce                |
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
#  * [2018/04/10]
#     - 본 모듈 작업 시작
################################################################################
# noinspection PyProtectedMember
from flask_restplus import Namespace, Resource
from flask import abort, request, current_app
# from vivans.store.pickle import PickleDB
from alabs.rest import parse_req_data, DEFAULT_LIMIT
from alabs.rest import get_keyval
from alabs.common.util.vvjson import safe_jsonify, convert_safe_str
from copy import deepcopy

################################################################################
__author__ = "MoonChang Chae <mcchae@gmail.com>"
__date__ = "2018/04/10"
__version__ = "1.18.0410"
__version_info__ = (1, 18, 418)
__license__ = "MIT"

################################################################################
# WITH_AAA = int(os.environ.get('WITH_AAA', '0'))


################################################################################
ns_api = Namespace('ns_rest', description='RESTful Template API')
json_parser = ns_api.parser()
json_parser.add_argument('json', type=str, location='json',
                         help='JSON BODY argument')
arg_parser = ns_api.parser()
arg_parser.add_argument('json', type=str,
                        help='URL JSON argument')


################################################################################
def on_load(app):
    pass


################################################################################
# noinspection PyMethodMayBeStatic
@ns_api.route('/ping')
class Ping(Resource):
    # ==========================================================================
    @ns_api.response(200, 'API Success/Failure')
    def get(self):
        """
        API ping to check alive or not

        # Input
        ## Arguments
        None

        # JSON Output
        ## Attributes
        * success : bool : required : Success or Failure
        * http_method : str : not required : http method on request
        * message : str : not required : error message on failure

        ### Response Sample
        ``` json
        {
            "success": true,
            "http_method": "GET"
        }
        ```
        """
        r = None
        try:
            r = {'success': True, 'http_method': request.method}
        except Exception as exp:
            r = {'success': False, 'message': str(exp)}
        finally:
            return r


################################################################################
# noinspection PyMethodMayBeStatic
@ns_api.route('/<string:collection>')
@ns_api.doc(params={'collection': 'pickleDB collection name'})
class Resources(Resource):
    """
    Resources
    """
    # ==========================================================================
    @ns_api.doc(parser=arg_parser)
    @ns_api.response(200, 'API Success/Failure')
    @ns_api.response(401, 'Authentication Error')
    # @cond_decorate(WITH_AAA, login_required)
    def get(self, collection):
        """
        <*RESTful*> get some or all documents from collection (resource)

        # Input
        ## Arguments

        ### In URL
        * collection : str : required : pickleDB collection name

        ### In json parameter
        * filter : dict : required : if omiited get all
        * skip : int : not required : offset from result documents
        * limit : int : not required : set number of documents
            if limit is not specified use DEFAULT_LIMIT instead
        * sort : int : not required : 1=ascending, -1=descending

        #### JSON Parameter Example
        ``` json
        {
            'filter': {'age': {'$gte': 100}},
            'skip': 2,
            'limit': 4,
            'sort': [('age', -1)]
        }
        ```

        # JSON Output
        ## Attributes
        * success : bool : required : true on success else false (when HTTP 200)
        * data : list : not required : on success list of rows
            which is document dict
        * total_count : int : not required : on success get the total number of
            documents (indended pagenation without offset or limit).
            But not implemented yet. **Just return the number or rows for now.**
        * message : str : not required : Failure message

        ### Response Sample
        ``` json
        {
            "success": true,
            "data": [
                { 'att1':'val1', 'att2':'val2' }
                { 'att1':'val3', 'att2':'val4' }
            ],
            "total_count": 2
        }
        ```
        """
        r = None
        try:
            # where condition may exists in request.args['json']
            # _filter = json.loads(request.args.get('json', '{}'))
            _filter = parse_req_data(request)
            if 'limit' not in _filter:
                _filter['limit'] = DEFAULT_LIMIT
            rows = [convert_safe_str(r) for r in
                    current_app.pickle.find(collection, **_filter)]
            tc_filter = deepcopy(_filter)
            if 'skip' in tc_filter:
                del tc_filter['skip']
            if 'limit' in tc_filter:
                del tc_filter['limit']
            # just get total count without skip, limit
            t_docs = [x for x in current_app.pickle.find(collection, **tc_filter)]
            total_count = len(t_docs)
            r = {'success': True, 'data': safe_jsonify(rows),
                 'total_count': total_count}
        except Exception as exp:
            r = {'success': False, 'message': str(exp)}
        finally:
            return r

    # ==========================================================================
    @ns_api.doc(parser=json_parser)
    @ns_api.response(200, 'API Success/Failure')
    @ns_api.response(401, 'Authentication Error')
    # @cond_decorate(WITH_AAA, login_required)
    def post(self, collection):
        """
        <*RESTful*> create a document into a collection (resource)

        # Input
        ## Arguments

        ### In URL
        * collection : str : required : pickleDB collection name

        ### In json parameter
        dict of a document

        #### JSON Parameter Example
        ``` json
        {
            "att1':'val1',
            'att2':'val2'
        }
        ```

        # JSON Output
        ## Attributes
        * success : bool : required : true on success else false (when HTTP 200)
        * data : dict : document dict to be inserted
        * message : str : not required : Failure message

        ### Response Sample
        ``` json
        {
            "success": true,
            "data": { 'att1':'val1', 'att2':'val2' }
        }
        ```
        """
        r = None
        try:
            p_json = parse_req_data(request)
            if not p_json:
                abort(400)
            _ = current_app.pickle.insert_one(collection, p_json)
            ret_list = [convert_safe_str(p_json)]
            r = {'success': True, 'data': ret_list}
        except Exception as exp:
            r = {'success': False, 'message': str(exp)}
        finally:
            return r

    # ========================================================================
    # noinspection PyUnusedLocal
    @ns_api.doc(parser=json_parser)
    @ns_api.response(200, 'API Success/Failure')
    @ns_api.response(401, 'Authentication Error')
    # @cond_decorate(WITH_AAA, login_required)
    def put(self, collection):
        """
        <*RESTful*> update some or all documents from collection (resource)

        # Input
        ## Arguments

        ### In URL
        * collection : str : required : pickleDB collection name

        ### In json parameter
        * sets : dict : required : column setting
            {"column1": "val1", "column2": "val2", ...}
        * filter : dict : required : if omiited update all

        #### JSON Parameter Example
        ``` json
        {
            'sets': {
                "column1':'val1',
                'column2':'val2'
            },
            'filter': {'age': {'$gte': 100}},
        }
        ```

        # JSON Output
        ## Attributes
        * success : bool : required : true on success else false (when HTTP 200)
        * updated_count : int : not required : on success updated count
        * message : str : not required : Failure message

        ### Response Sample
        ``` json
        {
            "success": true,
            "updated_count": 2
        }
        ```
        """
        r = None
        try:
            p_json = parse_req_data(request)
            if not p_json:
                abort(400)
            sets = {"$set": p_json['sets']}
            del p_json['sets']
            p_json['update'] = sets
            if 'filter' not in p_json:
                p_json['filter'] = {}
            if p_json:
                rc = current_app.pickle.update_many(collection, **p_json)
                r = {'success': True, 'updated_count': rc.modified_count}
            else:
                updated_count = current_app.pickle.count(collection)
                current_app.pickle.drop(collection)
                r = {'success': True, 'updated_count': updated_count}
        except Exception as exp:
            r = {'success': False, 'message': str(exp)}
        finally:
            return r

    # ==========================================================================
    @ns_api.doc(parser=json_parser)
    @ns_api.response(200, 'API Success/Failure')
    @ns_api.response(401, 'Authentication Error')
    # @cond_decorate(WITH_AAA, login_required)
    def delete(self, collection):
        """
        <*RESTful*> delete some or all documents from collection (resource)

        # Input
        ## Arguments

        ### In URL
        * collection : str : required : pickleDB collection name

        ### In json parameter
        * filter : dict : required : if omiited delete all

        #### JSON Parameter Example
        ``` json
        {
            'filter': {'age': {'$gte': 100}},
        }
        ```

        # JSON Output
        ## Attributes
        * success : bool : required : true on success else false (when HTTP 200)
        * deleted_count : int : not required : on success deleted count
        * message : str : not required : Failure message

        ### Response Sample
        ``` json
        {
            "success": true,
            "deleted_count": 2
        }
        ```
        """
        r = None
        try:
            # where condition may exists in request.args['json']
            # _filter = json.loads(request.args.get('json', '{}'))
            _filter = parse_req_data(request)
            if _filter:
                rc = current_app.pickle.delete_many(collection, **_filter)
                r = {'success': True, 'deleted_count': rc.deleted_count}
            else:
                deleted_count = current_app.pickle.count(collection)
                current_app.pickle.drop(collection)
                r = {'success': True, 'deleted_count': deleted_count}
        except Exception as exp:
            r = {'success': False, 'message': str(exp)}
        finally:
            return r


################################################################################
# noinspection PyMethodMayBeStatic
@ns_api.route('/<string:collection>/<int:doc_id>')
@ns_api.doc(params={'collection': 'pickleDB collection name',
                 'doc_id': 'string/integer document id'})
class ResourcesOne(Resource):
    """
    RestFul API /.../Resources/id like handler
    """
    # ==========================================================================
    @ns_api.response(200, 'API Success/Failure')
    @ns_api.response(401, 'Authentication Error')
    # @cond_decorate(WITH_AAA, login_required)
    def get(self, collection, doc_id):
        """
        <*RESTful*> get a document from collection (resource)

        # Input
        ## Arguments
        ### In URL
        * collection : str : required : pickleDB collection name
        * doc_id : int or str : required : if int then seek with _uid key
            else if doc_id has type of string and "keyname::=keyval" then
            seek from the keyname. *keyname must be indexed already using
            else raise RuntimeError*

        ### In json parameter
        None

        # JSON Output
        ## Attributes
        * success : bool : required : true on success else false (when HTTP 200)
        * data : dict : not required : on success a document dict *once this
            is a list but changed into dict (extract list)*
        * message : str : not required : Failure message

        ### Response Sample
        ``` json
        {
            "success": true,
            "data": { 'att1':'val1', 'att2':'val2' }
        }
        ```
        """
        r = None
        try:
            kn, kv = get_keyval(doc_id)
            ret = current_app.pickle.find_one(collection, {kn: kv})
            if ret:
                r = {'success': True, 'data': safe_jsonify(ret)}
            else:
                r = {'success': False, 'data': {}}
        except Exception as exp:
            r = {'success': False, 'message': str(exp)}
        finally:
            return r

    # ==========================================================================
    @ns_api.doc(parser=json_parser)
    @ns_api.response(200, 'API Success/Failure')
    @ns_api.response(400, 'Invalid parameter')
    @ns_api.response(401, 'Authentication Error')
    # @cond_decorate(WITH_AAA, login_required)
    def put(self, collection, doc_id):
        """
        <*RESTful*> update a document from collection (resource)

        # Input
        ## Arguments

        ### In URL
        * collection : str : required : pickleDB collection name
        * doc_id : int or str : required : if int then seek with _uid key
            else if doc_id has type of string and "keyname::=keyval" then
            seek from the keyname. *keyname must be indexed already using
            else raise RuntimeError*

        ### In json parameter
        dict of a document to update

        #### JSON Parameter Example
        ``` json
        {
            "att1':'val1',
            'att2':'val2'
        }
        ```

        # JSON Output
        ## Attributes
        * success : bool : required : true on success else false (when HTTP 200)
        * data : dict : not required : on success a document dict *once this
            is a list but changed into dict (extract list)*
        * message : str : not required : Failure message

        ### Response Sample
        ``` json
        {
            "success": true,
            "data": { 'att1':'val1', 'att2':'val2' }
        }
        ```
        """
        r = None
        try:
            p_json = parse_req_data(request)
            if not p_json:
                abort(400)
            kn, kv = get_keyval(doc_id)
            _ = current_app.pickle.update_one(collection,
                                             {kn: kv}, {'$set': p_json})
            ret = current_app.pickle.find_one(collection, {kn: kv})
            if ret:
                r = {'success': True, 'data': safe_jsonify(ret)}
            else:
                r = {'success': False, 'data': {}}
        except Exception as exp:
            r = {'success': False, 'message': str(exp)}
        finally:
            return r

    # ==========================================================================
    @ns_api.response(200, 'API Success/Failure')
    @ns_api.response(401, 'Authentication Error')
    # @cond_decorate(WITH_AAA, login_required)
    def delete(self, collection, doc_id):
        """
        <*RESTful*> delete a document from collection (resource)

        # Input
        ## Arguments
        ### In URL
        * collection : str : required : pickleDB collection name
        * doc_id : int or str : required : if int then seek with _uid key
            else if doc_id has type of string and "keyname::=keyval" then
            seek from the keyname. *keyname must be indexed already using
            else raise RuntimeError*

        ### In json parameter
        None

        # JSON Output
        ## Attributes
        * success : bool : required : true on success else false (when HTTP 200)
        * deleted_count : int : not required : on success deleted count (must 1)
        * message : str : not required : Failure message

        ### Response Sample
        ``` json
        {
            "success": true,
            "data": { 'att1':'val1', 'att2':'val2' }
        }
        ```
        """
        r = None
        try:
            kn, kv = get_keyval(doc_id)
            # delete_one => delete (many)
            rc = current_app.pickle.delete_many(collection, {kn: kv})
            r = {'success': True, 'deleted_count': rc.deleted_count}
        except Exception as exp:
            r = {'success': False, 'message': str(exp)}
        finally:
            return r


################################################################################
@ns_api.route('/<string:collection>/<string:doc_id>')
class ResourcesOneStr(ResourcesOne):
    pass

