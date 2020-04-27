import json

from alabs.common.util.vvtest import captured_output


def run_operation(*args, **kwargs):
    """
    ARGOS RPA 오퍼레이션 모듈 실행
    :param coord: func, (args_1, args_2)
    :return:
    """
    with captured_output() as (out, err):
        args[0](*args[1])
    out = out.getvalue()
    err = err.getvalue()
    if err:
        err = json.loads(err)
        return err
    out = json.loads(out)
    return out