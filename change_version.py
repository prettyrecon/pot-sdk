"""
====================================
 :mod:change_version
====================================
.. moduleauthor:: Jerry Chae <mcchae@argos-labs.com>
.. note:: ARGOS-LABS
"""

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
#  * [2018/12/08]
#     - normalize 옵션 추가
#  * [2018/12/06]
#     - 본 모듈 작업 시작
################################################################################
import os
import sys
import yaml
import datetime
import argparse


################################################################################
def change_version(yf, old_ver, new_ver):
    # with open(yf) as ifp:
    #     yfs = ifp.read()
    # with open(yf, 'w') as ofp:
    #     ofp.write(yfs.replace(old_ver, new_ver))
    now = datetime.datetime.now().strftime('%y%m%d-%H%M%S')
    with open(yf) as ifp:
        yc = yaml.load(ifp)
    yc['setup']['version'] = new_ver
    yc['setup']['classifiers'].\
        append('Topic :: Change :: Log :: Auto Build & Release at %s for %s' %
               (now, sys.platform))
    with open(yf, 'w') as ofp:
        yaml.dump(yc, ofp, default_flow_style=False)
    print('"%s" version: "%s" => "%s"' %(yf, old_ver, new_ver))
    return True


################################################################################
def get_version(yf):
    if not os.path.exists(yf):
        raise IOError('Cannot find setup.yaml "%s"' % yf)
    with open(yf) as ifp:
        yc = yaml.load(ifp)
        return yc['setup']['version']


################################################################################
def new_version(ver):
    now = datetime.datetime.now()
    now_v = '%s%s' % (now.year-2000, now.strftime('%m%d'))
    if not ver:
        ver = '0.1'
    if not isinstance(ver, str):
        ver = str(ver)
    vs = ver.split('.')
    if len(vs) < 4:
        while True:
            vs.append('0')
            if len(vs) == 4:
                break
    if len(vs) > 4:
        vs = vs[:4]
    if vs[2] != now_v:
        vs[2] = now_v
        vs[3] = '1'
    else:
        vs[3] = str(int(vs[3]) + 1)
    return '.'.join(vs)


################################################################################
def new_version_n(ver):
    now = datetime.datetime.now()
    now_v = '%s.%s' % (now.year-2000, now.strftime('%m%d'))
    if not ver:
        return '%s.10' % now_v
    vl = ver.split('.')
    if len(vl) != 3:
        return '%s.10' % now_v
    if '.'.join(vl[:2]) != now_v:
        return '%s.10' % now_v
    # noinspection PyBroadException
    try:
        # 무조건 이전 값의 다음 10
        inc = (int(vl[2]) + 10) // 10 * 10
    except Exception:
        inc = 10
    return '%s.%s' % (now_v, inc)


################################################################################
def parse_params():
    parser = argparse.ArgumentParser(
        description='''get version and change version:

Version changing rule is:
  version is seems like: 1.2.180123.8
  Only change third and forth version info (eg. 180123.08)

    180123.8
    ==
    Two digits of year

    180123.8
      ====
      Month and Day
    180123.8
           ==
           Sequence

  Howevery if '--normalize' or '-n' option is given
    18.1207.10
    ==
    Two digits of year

    18.1207.10
       ====
       Month and Day
    18.1207.10
            ==
            Sequence number of 10 times (10, 20, 30, ...)
            if previous is 5 then next is 10.
    above VERSION is set  

''', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--version', '-v', action='store',
                        help='version info like "1.2.18012308"')
    parser.add_argument('--normalize', '-n', action='store_true',
                        help='Normalized VERSION like "18.1207.10", '
                             'refer help')
    parser.add_argument('yamls', metavar='setup-file', nargs='+',
                        help='setup.yaml file path (one or more)')
    args = parser.parse_args()
    return args


################################################################################
if __name__ == '__main__':
    _args = parse_params()
    for yf in _args.yamls:
        ov = get_version(yf)
        if not _args.version:
            if _args.normalize:
                _args.version = new_version_n(ov)
            else:
                _args.version = new_version(ov)
        change_version(yf, ov, _args.version)
