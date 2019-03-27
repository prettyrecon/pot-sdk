#!/usr/bin/env python
# coding=utf8

###############################################################################
import os
import pickle
# noinspection PyPackageRequirements
from miracle.acl import Acl
# from pprint import pformat

WITH_AAA = int(os.environ.get('WITH_AAA', '0'))


###############################################################################
class AuthorizationError(Exception):
    pass


###############################################################################
class RoleResourcePermission(object):
    # =========================================================================
    PKL_FILE = '%s.rrp' % os.path.abspath(os.path.basename(__file__))

    # =========================================================================
    def __init__(self):
        self.acl = None
        self.load()

    # =========================================================================
    def __repr__(self):
        # r = pformat(self.acl.__getstate__())
        sl = list()
        sl.append('roles=[')
        for role in self.get_roles():
            sl.append("  '%s'=[" % role)
            for res, perm in self.acl.which(role).items():
                sl.append('    %s : %s' % (res, perm))
            sl.append('  ]')
        sl.append(']')
        return '\n'.join(sl)

    # =========================================================================
    def save(self):
        with open(self.PKL_FILE, 'wb+') as ofp:
            pickle.dump(self.acl.__getstate__(), ofp)

    # =========================================================================
    def load(self):
        self.acl = Acl()
        if os.path.exists(self.PKL_FILE):
            with open(self.PKL_FILE, 'rb+') as ifp:
                d = pickle.load(ifp)
            self.acl.__setstate__(d)
        else:
            self.acl.grants({
                'admin': {
                    'all': {'all'}
                }
            })

    # =========================================================================
    def add(self, gr):
        self.acl.grants(gr)
        self.save()

    # =========================================================================
    def clear(self):
        if os.path.exists(self.PKL_FILE):
            os.remove(self.PKL_FILE)
        self.load()

    # =========================================================================
    def _check(self, role, resource, permission):
        rp = self.acl.which(role)
        if 'all' in rp.keys():
            return True
        return self.acl.check(role, resource, permission)

    # =========================================================================
    def check(self, roles_or_role, resource, permission='all',
              raise_exception=True):
        if not WITH_AAA:
            return False
        if isinstance(roles_or_role, (list, tuple)):
            for role in roles_or_role:
                r = self._check(role, resource, permission)
                if r:
                    return r
        else:
            r = self._check(roles_or_role, resource, permission)
            if r:
                return r
        if raise_exception:
            raise AuthorizationError('Role<%s> has no Permission<%s> '
                                     'to Resource<%s>' %
                                     (roles_or_role, permission, resource))
        return False

    # =========================================================================
    def get_roles(self):
        return list(self.acl.get_roles())

    # =========================================================================
    def isin_roles(self, role):
        return role in self.get_roles()

    # =========================================================================
    def get_resources(self, role=None):
        if not role:
            return list(self.acl.get_resources())
        if role not in self.get_roles():
            return []
        return list(self.acl.which(role).keys())

    # =========================================================================
    def isin_resources(self, role, resource):
        if not self.isin_roles(role):
            return False
        return resource in self.get_resources(role)

    # =========================================================================
    def get_permissions(self, role, resource):
        # return self.acl.get_permissions(resource)
        if not role or role not in self.get_roles():
            return []
        if not resource or resource not in self.get_resources(role):
            return []
        return list(self.acl.which(role)[resource])

    # =========================================================================
    def isin_permissions(self, role, resource, permission):
        if not self.isin_resources(role, resource):
            return False
        return permission in self.get_permissions(role, resource)


###############################################################################
def acl_test():
    # =========================================================================
    rrp = RoleResourcePermission()
    # =========================================================================
    gr = {
        'root': {
            'all': ['all']
        },
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
    rrp.add(gr)
    # =========================================================================
    print('rrp=%s' % rrp)
    # =========================================================================
    # 해당되는 role:resource:read 가 가능한가 조사 : 없는 역할,리소스 등은 모두 False
    check_arg = ('no_role', 'no_resource', 'read')
    print('check for %s = %s' % (check_arg,
                                 rrp.check(*check_arg, raise_exception=False)))
    # 해당되는 role:resource:read 가 가능한가 조사: 가능한 역할,리소스의 권한체크
    check_arg = ('root', 'page_user', 'read')
    print('check for %s = %s' % (check_arg,
                                 rrp.check(*check_arg, raise_exception=False)))
    # 해당되는 role:resource:read 가 가능한가 조사: 가능한 역할,리소스의 권한체크
    check_arg = ('users', 'page_root', 'read')
    print('check for %s = %s' % (check_arg,
                                 rrp.check(*check_arg, raise_exception=False)))
    # 해당되는 role:resource:read 가 가능한가 조사: 불가능한 역할,리소스의 권한체크
    check_arg = ('users', 'page_root', 'write')
    print('check for %s = %s' % (check_arg,
                                 rrp.check(*check_arg, raise_exception=False)))
    # =========================================================================
    # 특정 역할:자원:권한 추가
    add_gr = {
        'operators': {
            'page_user': ['read', 'write', 'create', 'delete'],
            'page_guest': ['read', 'write', 'create', 'delete'],
        },
        'users': {
            'test_user': ['read', 'write', 'create', 'delete'],
            'page_guest': ['read', 'write', 'create', 'delete', 'all'],
        }
    }
    rrp.add(add_gr)
    print('after added=%s' % rrp)
    # =========================================================================
    print('get_roles=%s' % rrp.get_roles())
    # =========================================================================
    print('get_resources("users")=%s' % rrp.get_resources("users"))
    print('isin_roles("users")=%s' % rrp.isin_roles("users"))
    # =========================================================================
    print('get_resources("users_xx")=%s' % rrp.get_resources("users_xx"))
    print('isin_roles("users_xx")=%s' % rrp.isin_roles("users_xx"))
    # =========================================================================
    print('get_permissions("users", "page_guest")=%s'
          % rrp.get_permissions("users", "page_guest"))
    print('isin_resources("users", "page_guest")=%s'
          % rrp.isin_resources("users", "page_guest"))
    # =========================================================================
    print('get_permissions("users", "page_guest2")=%s'
          % rrp.get_permissions("users", "page_guest2"))
    print('isin_resources("users", "page_guest2")=%s'
          % rrp.isin_resources("users", "page_guest2"))
    # =========================================================================
    print('isin_permissions("users", "api_rest", "delete")=%s'
          % rrp.isin_permissions("users", "api_rest", "delete"))
    print('isin_permissions("users", "api_rest", "myp")=%s'
          % rrp.isin_permissions("users", "api_rest", "myp"))

    # =========================================================================
    rrp.clear()
    print('after clear=%s' % rrp)


###############################################################################
if __name__ == '__main__':
    acl_test()
