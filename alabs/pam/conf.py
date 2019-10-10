import os
import json
import pathlib
import yaml

from alabs.common.util.vvjson import set_xpath
from alabs.common.util.vvjson import get_xpath


path = dict()
ARGOS_RPA_PAM_DIR = pathlib.Path.home() / '.argoslabs-rpa'
PAM = ARGOS_RPA_PAM_DIR / 'pam'
ARGOS_RPA_BOTS_DIR = PAM / 'bots'
ARGOS_RPA_PAM_LOG_DIR = PAM / "logs"
ARGOS_RPA_VENV_DIR = ARGOS_RPA_PAM_DIR / "venvs"
# PosixPath('/Users/limdeokyu/.argos-rpa.logs')

# PosixPath('/Users/limdeokyu/.argos-rpa.logs/17880')
CURRENT_PAM_CONF_DIR = PAM
CURRENT_PAM_LOG_DIR = ARGOS_RPA_PAM_LOG_DIR


path['PAM_CONF'] = str(CURRENT_PAM_CONF_DIR / "pam.conf")
path['USER_PARAM_VARIABLES'] = str(CURRENT_PAM_CONF_DIR /
                                   "user_param_variables.json")

path["CURRENT_PAM_LOG_DIR"] = str(CURRENT_PAM_LOG_DIR)
path["OPERATION_STDOUT_FILE"] = str(CURRENT_PAM_LOG_DIR / "operation.stdout")
path["OPERATION_STDERR_FILE"] = str(CURRENT_PAM_LOG_DIR / "operation.stderr")
path["PLUGIN_LOG"] = str(CURRENT_PAM_LOG_DIR / "plugin.log")
path["PLUGIN_STDOUT_FILE"] = str(CURRENT_PAM_LOG_DIR / "plugin.stdout")
path["PLUGIN_STDERR_FILE"] = str(CURRENT_PAM_LOG_DIR / "plugin.stderr")
path["PAM_LOG"] = str(CURRENT_PAM_LOG_DIR / "pam.log")
path["OPERATION_LOG"] = str(CURRENT_PAM_LOG_DIR / "operation.log")


manager = dict()
manager['IP'] = '127.0.0.1'
manager['PORT'] = 8012
manager['LOG_LEVEL'] = 'info'
manager['VARIABLE_MANAGER_IP'] = '127.0.0.1'
manager['VARIABLE_MANAGER_PORT'] = 8012

_conf = {
        'PATH': path,
        'MANAGER': manager,
    }


class Config(dict):
    def __init__(self, logger=None, **kwargs):
        dict.__init__(self, **kwargs)
        self.logger = logger

    def get(self, xpath):
        """
        설정 값을 xpath 위치의 것을 반환
        값이 존재하지 않는다면 '추가된 값'이 있다고 판단,
        기본 값을 가져와서 저장 및 반환
        :param xpath:
        :return: value
        """
        try:
            return get_xpath(self, xpath, raise_exception=True)
        except ReferenceError:
            v = get_xpath(_conf, xpath)
            if v is None:
                raise KeyError('{} is not '.format(xpath))
            set_xpath(self, xpath, v)
            conf_path = os.environ.setdefault('PAM_CONF', path['PAM_CONF'])
            write_conf_file(conf_path, dict(self))
            if self.logger:
                self.logger.info('Inserted default setting values... ')
                d = json.dumps({'PAM_LOG': path, 'XPATH': path, 'VALUE': v})
                self.logger.debug(d)
        return v


def set_environment(keys):
    for key in _conf[keys]:
        os.environ[key] = _conf['PATH'][key]


def get_conf_from_file(path):
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    return data


def write_conf_file(path, data):
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)


def get_conf(logger=None):
    # 설정 파일
    if not os.environ.setdefault('PAM_CONF', ''):
        path = pathlib.Path.home() / '.argos-rpa-pam.conf'
        os.environ['PAM_CONF'] = str(path)

    if not pathlib.Path(os.environ['PAM_CONF']).exists():
        global _conf
        write_conf_file(os.environ['PAM_CONF'], _conf)
        if logger:
            logger.info('PAM\' config file is not existed. '
                        'New config with default setting file is written.')
    env = get_conf_from_file(os.environ['PAM_CONF'])
    config = Config(logger)
    config.update(env)
    return config

