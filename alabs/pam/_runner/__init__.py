import sys
import os
import time
from functools import wraps

REST_API_PREFIX = 'api'
REST_API_VERSION = 'v1.0'
REST_API_NAME = 'pam'

################################################################################
# 코루틴 타이머
# 타이머인스턴스.send(n) 을 이용하여 시간을 추가
def is_timeout(t):
    st = int(time.time()) + t
    while int(time.time()) < st:
        time.sleep(0.01)
        t = yield st - int(time.time())
        if t:
            st += t


################################################################################
def activate_virtual_environment(f):
    # 멀티프로세싱에서 데코레이터를 사용하기 위해서 functools.wraps를 사용
    @wraps(f)
    def func(*args, **kwargs):
        exec_path = sys.executable

        # 패스 설정
        old_os_path = os.environ.get('PATH', '')
        os.environ['PATH'] = os.path.dirname(
            os.path.abspath(exec_path)) + os.pathsep + old_os_path
        base = os.path.dirname(os.path.dirname(os.path.abspath(exec_path)))

        # 플랫폼에 따른 site-packages 위치
        if sys.platform == 'win32':
            site_packages = os.path.join(base, 'Lib', 'site-packages')
        else:
            site_packages = os.path.join(base, 'lib',
                                         'python%s' % sys.version[:3],
                                         'site-packages')
        # site-package 추가
        prev_sys_path = list(sys.path)
        import site

        site.addsitedir(site_packages)
        sys.real_prefix = sys.prefix
        sys.prefix = base

        new_sys_path = []
        # 패스 우선순위 변경
        for item in list(sys.path):
            if item not in prev_sys_path:
                new_sys_path.append(item)
                sys.path.remove(item)
        sys.path[:0] = new_sys_path

        # 실제 함수 실행
        f(*args, **kwargs)
    return func
