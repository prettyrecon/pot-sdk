import sys
import os
import time
import pathlib
import copy
import enum
import datetime

from functools import wraps
import multiprocessing as mp

from alabs.pam.variable_manager.rc_api_variable_manager import \
    VariableManagerAPI
from alabs.common.util.vvlogger import get_logger


################################################################################
class ResultAction(enum.Enum):
    MoveOn = 'Go'
    TreatAsError = 'Error'
    IgnoreFailure = 'FinishStep'
    AbortScenarioButNoError = 'FinishScenario'
    JumpForward = 'Jump'
    JumpBackward = 'BackJump'
    JumpToOperation = 'Goto'
    JumpToStep = 'StepJump'
    RestartFromTop = 'Restart'


################################################################################
class ResultHandler(enum.Enum):

    # ==========================================================================
    SCENARIO_SET_ITEM = "_result_handler_set_item"
    SCENARIO_SET_STEP = "_result_handler_set_step"
    SCENARIO_JUMP_FORWARD = "_result_handler_jump_forward"
    SCENARIO_JUMP_BACKWARD = "_result_handler_jump_backward"
    SCENARIO_FINISH_STEP = '_result_handler_finish_step'
    SCENARIO_FINISH_SCENARIO = '_result_handler_finish_scenario'
    # ==========================================================================
    VARIABLE_SET_VALUES = '_result_handler_set_variables'


################################################################################
class ExceptionTreatAsError(Exception):
    pass


################################################################################
class StatusMessage(dict):
    # ==========================================================================
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)
        self.time = time.time()
        self['time'] = self.time

    def set_status(self, code, status, info: dict, message):
        self['code'] = code
        self['status'] = status
        self.update(info)
        self['message'] = message


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
def get_env():
    env = list()
    ARGOS_RPA_VENV_DIR = pathlib.Path.home() / ".argos-rpa.venv"
    ARGOS_RPA_BOTS_DIR = pathlib.Path.home() / ".argos-rpa.bots"
    # PosixPath('/Users/limdeokyu/.argos-rpa.logs')
    ARGOS_RPA_PAM_LOG_DIR = pathlib.Path.home() / ".argos-rpa.logs"
    # PosixPath('/Users/limdeokyu/.argos-rpa.logs/17880')
    CURRENT_PAM_LOG_DIR = ARGOS_RPA_PAM_LOG_DIR
    # CURRENT_PAM_LOG_DIR = ARGOS_RPA_PAM_LOG_DIR / str(os.getpid())

    env.append(("CURRENT_PAM_LOG_DIR", str(CURRENT_PAM_LOG_DIR)))
    env.append(('USER_PARAM_VARIABLES',
                str(CURRENT_PAM_LOG_DIR / "user_param_variables.json")))
    env.append(("OPERATION_STDOUT_FILE",
                str(CURRENT_PAM_LOG_DIR / "operation.stdout")))
    env.append(("PLUGIN_STDOUT_FILE",
                str(CURRENT_PAM_LOG_DIR / "plugin.stdout")))
    env.append(("PLUGIN_STDERR_FILE",
                str(CURRENT_PAM_LOG_DIR / "plugin.stderr")))
    env.append(("PAM_LOG", str(CURRENT_PAM_LOG_DIR / "pam.log")))
    return env


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

        # 환경변수 설정
        for env in get_env():
            os.environ[env[0]] = env[1]

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


################################################################################
class Runner(mp.Process):
    class Status(enum.Enum):
        IDLE = 'Idle'
        PREPARING = 'Preparing'
        RUNNING = 'Running'
        PAUSING = 'Pausing'
        STOPPING = 'Stopping'

    class Code(enum.Enum):
        NORMAL = "Normal"
        ERROR = "Error"

    def __init__(self, scenario, pipe, event, *args, **kwargs):
        # super(Runner, self).__init__(*args, **kwargs)
        super(Runner, self).__init__()
        self._name = str(os.getpid())
        self.logger = None

        self.created_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self._venv_path = None
        self._scenario_name = None
        self._scenario = scenario if scenario else None
        self._variables = None
        self._pipe = pipe
        self._event = event

        self._breakpoints = set()
        self._debug_step_over = False

        self._pause = True
        self.status_message = StatusMessage()


    @property
    def name(self):
        return self._name

    # BOT(Scenario) 관련 =======================================================
    @property
    def scenario(self):
        return self._scenario

    @scenario.setter
    def scenario(self, scenario_file: str):
        self._scenario = scenario_file

    def get_init_scenario(self):
        return copy.deepcopy(self.scenario)

    # 파이썬 가상환경 프로퍼티 ===================================================
    @property
    def venv_path(self):
        if not self._venv_path:
            return None
        return str(self._venv_path)

    @venv_path.setter
    def venv_path(self, path):
        self._venv_path = pathlib.Path(path)

    @property
    def venv_python(self):
        if not self.venv_path:
            return None
        # TODO: Platform 별로 나눠야 함
        path = self.venv_path / pathlib.Path('bin/python')
        return str(path)

    # 브레이크 포인트 ===========================================================
    @property
    def break_points(self) -> tuple:
        return tuple(self._breakpoints)

    @break_points.setter
    def break_points(self, bp: list):
        self.logger.info("Set breakpoints... {}".format(str(bp)))
        # 같은 값이 또 들어오면 삭제, 없는 값이면 추가
        self._breakpoints ^= set(bp)

    def is_break_point(self, cur: tuple, bp_list: tuple):
        cur = hash(cur)
        for bp in bp_list:
            if hash(bp) == cur:
                return True
        return False

    # ==========================================================================
    @property
    def pause(self):
        return self._pause

    # ==========================================================================
    def stop(self, *args):
        # 현재 진행 중이던 시나리오를 멈추고 새로 돌 수 있게 준비
        # iterator 방식으로 시나리오가 진행되기 때문에 새로운 시나리오 인스턴스 생성
        # self._load_scenario(self.scenario_filename)
        self.logger.info("Set status as STOP")
        time.sleep(0.1)
        self._pause = True

    # ==========================================================================
    def _call_item(self, item):
        info = "{step} / {operator} "
        # Status Message
        self.status_message.set_status(
            self.Code.NORMAL.value, self.Status.RUNNING.value,
            self.scenario.info,
            "Running... " + info.format(**self._scenario.info))
        # 액션 실행 전 딜레이
        tm = int(item['beforeDelayTime'])
        time.sleep(tm * 0.001)
        self.logger.info("Delay before run item for {}".format(str(tm * 0.001)))
        self._pipe.send(self.status_message)
        # 아이템 실행
        time.sleep(2)
        return item()

    # ==========================================================================
    def play(self):
        self.logger.info("Set status as PLAY")
        self._pause = False
        return self._pause

    # ==========================================================================
    def _is_pause_needed(self):
        # 일반적인 디버그모드의 `스텝오버` 기능
        if self._debug_step_over:
            self._pause = True
        # 브레이크 포인트
        cur_idx = (self._scenario.current_step_index,
                   self._scenario.current_item_index)
        if self.is_break_point(cur_idx, self.break_points):
            self._pause = True
            # 위의 어떠한 조건이라도 만족한 경우 `멈춤`
            # 탈출 조건은 `시작` 요청에 의한 self._pause의 False 전환

            # Status Message
            # self.status_message.set_status(
            #     self.Code.NORMAL.value, self.Status.PAUSING.value,
            #     self._scenario.info, "Pausing")
            # print(self.status_message)
        time.sleep(0.1)
        return self._pause

    # ==========================================================================
    def _follow_up(self, data):
        # data = {
        #     "status": "OK",
        #     "function": (ResultHandler, args),
        # }
        # 처리 우선순위
        # data 존재여부 > status 상태 >
        if not data:
            return
        if not data['status']:
            raise ExceptionTreatAsError(data['message'])
        if data['status'] and not data['function']:
            return
        if not hasattr(self, data['function'][0]):
            raise ValueError
        f = getattr(self, data['function'][0])
        ret = f(data['function'][1])
        return ret

    # ==========================================================================
    @activate_virtual_environment
    def run(self, *args, **kwargs):
        self.logger = get_logger(os.environ.setdefault('PAM_LOG', 'runner.log'))
        self.logger.info("Runner Started")
        if not self.scenario:
            self.logger.error("Bot must be set before running.")
            raise Exception("A BOT HAS TO BE SET BEFORE RUN.")

        # 변수 초기화
        self.init_variables()
        # self._scenario.__iter__()
        try:
            while not self._event.is_set():
                # 타이머 추가 필요.
                # 명령어 우선 처리
                if self._pipe.poll():
                    cmd, *args = self._pipe.recv()
                    self.logger.info("Command Received... {}({})".format(cmd, str(args)))
                    ret = getattr(self, cmd)(*args)

                    self._pipe.send(ret)
                    continue

                if self._is_pause_needed():
                    continue

                # 아이템 실행
                item = next(self.scenario)
                # TODO: 후속처리 필요
                data = self._call_item(item)
                self._follow_up(data)

                # Status Message
                # self.status_message.set_status(
                #     self.Code.NORMAL.value, self.Status.STOPPING.value,
                #     self._scenario.info, "The scenario is done.")
                # print(self.status_message)
                time.sleep(0.1)

        except StopIteration:
            pass
        except ExceptionTreatAsError as e:
            print(e)
        except KeyboardInterrupt:
            print("Keyboard Int")
        except Exception as e:
            print("Exception!!!!")
            import traceback
            traceback.print_exc()
            print(e)
        finally:
            print(self.pid, "is done")
            self._event.set()
        return

    # ==========================================================================
    def init_variables(self):
        """
        변수매니져와 연결 및 변수 선언
        :return:
        """
        self.logger.info('Start initializing variables...')
        pid = os.getpid()
        try:
            self._variables = VariableManagerAPI(pid=pid, logger=self.logger)

            # 봇 필수 변수 선언
            self.logger.info("Declared Essential Variables...")
            self._variables.create('{{rp.index}}', value=0)  # Loop Index
            self._variables.create('{{saved_data}}', value=" ")  # Saved Data

            # 사용자 변수 선언
            self.logger.info("Declared User Variables...")
            variable_list = self.scenario['userVariableList']
            for var in variable_list:
                variable = "{{%s.%s}}" % (var['GroupName'], var['VariableName'])
                self._variables.create(variable, None)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.logger.info("ERROR: Initialize Variable - {}".format(str(e)))
            raise Exception
        self.logger.info('End Initializing variables...')

    # 아이템 실행결과에 따른 다음 동작
    # ResultHandler Scenario 관련
    # ==========================================================================
    def _result_handler_set_step(self, args):
        self.scenario.step = args[0]

    # ==========================================================================
    def _result_handler_set_item(self, args):
        self.scenario.set_current_item_by_index(int(args[0]))

    # ==========================================================================
    def _result_handler_finish_step(self, args):
        self.scenario.next_step()

    # ==========================================================================
    def _result_handler_jump_forward(self, args):
        self.scenario.forward(int(args[0]))

    # ==========================================================================
    def _result_handler_jump_backward(self, args):
        self.scenario.backward(int(args[0]))

    # ==========================================================================
    def _result_handler_finish_scenario(self, args):
        self.scenario.finish_scenario()

    # ResultHandler Variable 관련
    # ==========================================================================
    def _result_handler_set_variables(self, args):
        for name, value in args:
            self._variables.create(name, value)








