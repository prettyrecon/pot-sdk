"""
====================================
 :mod:alabs.pymgr.pimgr ARGOS-LABS Python VENV-Plugin Manager
====================================
.. moduleauthor:: Jerry Chae <mcchae@argos-labs.com>
.. note:: ARGOS-LABS
"""

# 작업 내용
# =========
#
#
#  alabs.pymgr.vmmgr 에 의해 관리되는 특정 플러그인/버전에 대한 관리
#  -
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
#  * [2019/08/3]
#     - 본 모듈 작업 시작
################################################################################

import os
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler


################################################################################
def start_xmlrpc_server(rpc_path, port, instance, bind_addr='localhost'):
    # ==========================================================================
    class RequestHandler(SimpleXMLRPCRequestHandler):
        rpc_paths = ('/RPC2',)
    # ==========================================================================
    # Create server
    with SimpleXMLRPCServer((bind_addr, int(port)),
                            requestHandler=RequestHandler) as server:
        server.register_introspection_functions()
        server.register_instance(instance)
        # Run the server's main loop
        server.serve_forever()


class MyFuncs:
    def mul(self, x, y):
        return x * y


################################################################################
if __name__ == '__main__':

    start_xmlrpc_server('/RPC2', 8000, MyFuncs())
