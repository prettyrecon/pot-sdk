"""
====================================
 :mod:alabs.pymgr ARGOS-LABS Python Manager
====================================
.. moduleauthor:: Jerry Chae <mcchae@argos-labs.com>
.. note:: ARGOS-LABS
"""

# 작업 내용
# =========
#
# 기존에 PPM 관련 작업이 너무 시간이 걸리는 결과 다음과 같은 것을을
# 서비스로 담고 있으면서 (또는 백그라운드 작업을 진행하면서) 서비스 하도록 함
# - alabs.ppm 관련 서비스
# - get/make venv 관련 서비스
# - prepare propper plugin(with specfic version) in venv and call and return
#   result promptly
# - download propper plugins as a background job in venv
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
#  * [2019/07/31]
#     - 본 모듈 작업 시작
################################################################################

