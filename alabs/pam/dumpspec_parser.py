import os
import json


################################################################################
def cast_type(t, v):
    """
    :param t: type
    :param v: value
    :return:
    """
    if t == 'str':
        return '"' + v + '"'
    return str(v)


################################################################################
def store(v):
    """
    :param v:
    :return: ['hello',] or ['--example', 'hello']
    """
    ret = list()
    if v['value']:
        ret.append(cast_type(v['type'], v['value']))
    elif v['default']:
        ret.append(cast_type(v['type'], v['default']))
    else:
        return None
    if len(v['option_strings']):
        ret.insert(0, v['option_strings'][0])
    return ret


################################################################################
def storeconst(v):
    """
    :param v:
    :return: ['--option'] or None
    """
    if v['value'] != "True":
        return None
    if v['const'] is None:
        raise ValueError
    return [v['option_strings'][0], ]


################################################################################
def storetrue(v):
    """
    :param v:
    :return: ['--option'] or None
    """
    if v['value'] != 'True':
        return None
    return [v['option_strings'][0], ]


################################################################################
def storefalse(v):
    """
    :param v:
    :return:
    """
    if v['value'] != 'False':
        return None
    return [v['option_strings'][0], ]


################################################################################
def append(v):
    """
    :param v:
    :return: ['--example', 'A', '--example', 'B '--example', 'C']
    """
    delimiter = '|*|*|'
    if not v['value']:
        return None
    vs = v['value'].split(delimiter)
    ret = list()
    for value in vs:
        ret.append(v['option_strings'][0])
        ret.append(value)
    return ret


################################################################################
def count(v):
    """
    :param v:
    :return:   ['--example', '--example', '--example']
    """

    n = int(v['value'])
    if not n:
        return None

    opt = v['option_strings'][1][1]  # -e 에서 e 만 가져옴
    ret = "-{}".format(opt * n)
    return [ret, ]


################################################################################
def get_plugin_dumpspec(dumpspec):
    return json.loads(dumpspec)


################################################################################
def plugin_spec_parser(dumpspec: dict):
    # 플러그인 실행과 관련없는 항목
    exclude_specs = ('dumpspec', 'help', 'outfile', 'infile', 'errfile',
                    'statfile', 'logfile', 'loglevel', 'verbose', 'fileread',)

    # JSON 포맷인 DumpSpec 을 가져오기
    spec = get_plugin_dumpspec(dumpspec)

    args = list()
    # 필수 파라메터와 옵션 스펙을 분석하여 CLI용 파라메터 생성
    for param in spec['parameters']:
        # action 과 같은 이름의 함수 호출
        v = globals()[param['action']](param)
        if not v:
            continue
        args += v

    for param in spec['options']:
        if param['name'] in exclude_specs:
            continue
        v = globals()[param['action']](param)
        if not v:
            continue
        args += v

    stdout = os.environ.setdefault('PLUGIN_STDOUT_FILE', 'plugin_stdout.log')
    if stdout:
        args += ['--outfile ', stdout]

    pam_log = os.environ.setdefault('PAM_LOG', 'pam.log')
    if pam_log:
        args += ['--errfile ', pam_log]
        args += ['--logfile', pam_log]

    ret = [spec['name'], ] + args
    ret = list(filter(None, ret))
    ret = ' '.join(ret)
    return ret
