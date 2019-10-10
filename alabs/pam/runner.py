import sys
import os
import time
import pathlib
import copy
import enum
import datetime
import site

from functools import wraps
import multiprocessing as mp
import traceback
import platform

from alabs.pam.scenario import Scenario
from alabs.common.definitions.platforms import Platforms
from alabs.pam.variable_manager.rc_api_variable_manager import \
    VariableManagerAPI
from alabs.common.util.vvlogger import get_logger, StructureLogFormat, \
    LogMessageHelper
from alabs.common.util.vvtest import captured_output
from alabs.pam.conf import get_conf


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
    SCENARIO_GOTO = '_result_handler_goto'

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
def activate_virtual_environment(f):
    # 멀티프로세싱에서 데코레이터를 사용하기 위해서 functools.wraps를 사용
    @wraps(f)
    def func(*args, **kwargs):
        logger = get_logger(get_conf().get('/PATH/PAM_LOG'))
        logger.info('Activating the virtual environment for the runner...')
        exec_path = sys.executable

        # 패스 설정
        old_os_path = os.environ.get('PATH', '')
        old_python_path = os.environ.setdefault('PYTHONPATH', '')

        os.environ['PATH'] = os.path.dirname(
            os.path.abspath(exec_path)) + os.pathsep + old_os_path
        base = os.path.dirname(os.path.dirname(os.path.abspath(exec_path)))

        # 환경변수 설정
        for env in get_conf().get('/PATH').items():
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
        if sys.platform == 'win32':
            sys.path.insert(0, sys.path.pop(1))
            os.environ['PYTHONPATH'] = ''
            pp = list()
            pp.append(sys.path[0])
            if old_python_path:
                pp += old_python_path.split(';')
            os.environ['PYTHONPATH'] = ';'.join(pp)

        logger.debug(StructureLogFormat(
            PARENT_PATH=old_os_path,
            PARENT_PYTHONPATH=old_python_path,
            SITE_PACKAGES=site_packages,
            RUNNER_PATH=os.environ['PATH'],
            RUNNER_PYTHONPATH=os.environ['PYTHONPATH']))

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
        self.logger = get_logger(get_conf().get('/PATH/PAM_LOG'))
        self.log_prefix = LogMessageHelper()

        self.created_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self._venv_path = None
        self._scenario_name = None
        self._scenario_path = None
        self._scenario = scenario if scenario else None
        self._variables = None
        self._pipe = pipe
        self._event = event
        self._run = True

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

    @property
    def scenario_path(self):
        return self._scenario_path

    @scenario_path.setter
    def scenario_path(self, path):
        self._scenario_path = path

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

        _platform = os.environ.get('ARGOS_RPA_PAM_PLATFORM', platform.system())
        if _platform == Platforms.WINDOWS.value:
            path = self.venv_path / pathlib.Path('Scripts/python.exe')
        else:
            path = self.venv_path / pathlib.Path('bin/python')
        return str(path)

    # 브레이크 포인트 ===========================================================
    @property
    def break_points(self) -> tuple:
        return tuple(self._breakpoints)

    @break_points.setter
    def break_points(self, bp: list):
        self.logger.info(self.log_prefix.format("Set breakpoints... "))
        self.logger.debug(StructureLogFormat(STREQUEST_BREAK_POINTS=bp))
        # 같은 값이 또 들어오면 삭제, 없는 값이면 추가
        self._breakpoints ^= set(bp)
        self.logger.debug(StructureLogFormat(CURRENT_BREAK=self._breakpoints))

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
        self.logger.info(self.log_prefix.format("Set status as STOP"))
        time.sleep(0.1)
        self._pause = True

    # ==========================================================================
    def _call_item(self, item):
        # 액션 실행 전 딜레이
        tm = int(item['beforeDelayTime'])
        self.logger.info(self.log_prefix.format(
            "Delaying before running the item"))
        self.logger.debug(StructureLogFormat(
            BEFORE_DELAY_MSEC=int(item['beforeDelayTime'])))
        time.sleep(tm * 0.001)

        # 아이템 실행
        result = item()
        return result

    # ==========================================================================
    def play(self):
        self.logger.info(self.log_prefix.format("Set status as PLAY"))
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
        self.logger.info(self.log_prefix.format(
            'Calling the result job function.'))
        self.logger.debug(FUNCTION=data['function'][0],
                          ARGUMENTS=data['function'][1])
        f = getattr(self, data['function'][0])
        ret = f(data['function'][1])
        return ret

    # ==========================================================================
    @activate_virtual_environment
    def run(self, *args, **kwargs):
        """
        새로운 파이썬 가상환경을 적용한 상태로 프로세스 시작
        :param args:
        :param kwargs:
        :return:
        """
        self.logger = get_logger(get_conf().get('/PATH/PAM_LOG'))
        self.log_prefix = LogMessageHelper(logger=self.logger)
        self.log_prefix.clear()
        self.log_prefix.push('Runner')

        self.logger.debug(StructureLogFormat(
            PYTHONPATH=os.environ.setdefault('PYTHONPATH', ''),
            PATH=os.environ.setdefault('PATH', '')))

        try:
            self.log_prefix.push('Preparing')
            # TODO: PIPE에 뭐가 들어있을지 알 수 없음
            scenario_path = self._pipe.recv()
            scenario = Scenario()
            scenario.load_scenario(scenario_path)
            self.scenario = scenario
            if not self.scenario:
                self.logger.error(self.log_prefix.format(
                    "Scenario must be set before running."))
            # 변수 초기화
            self.log_prefix.push('Initializing Variables')
            self.init_variables()
            self.log_prefix.pop()  # Initializing Variables
            self.log_prefix.pop()  # Preparing


            # 시나리오 루틴 시작 ================================================
            while self._run:
                # TODO: 타이머 추가 필요.
                # 명령어 우선 처리
                if self._pipe.poll():
                    self.log_prefix.push('Command Call Processing')
                    self.logger.info(self.log_prefix.format(
                        'Received command and arguments.'))
                    cmd, *args = self._pipe.recv()
                    self.logger.debug(StructureLogFormat(PIPE_CMD=cmd,
                                                         PIPE_ARGS=args))
                    ret = getattr(self, cmd)(*args)
                    self._pipe.send(ret)
                    self.log_prefix.pop()  # Command Call Processing
                    continue

                # 잠시 멈춤이 필요한지 검사.
                # 잠시 멈춤 요구, 브레이크 포인트 등.
                if self._is_pause_needed():
                    continue

                # 아이템 실행
                self.log_prefix.push('Scenario Stepping')
                item = next(self.scenario)
                if item['Disabled']:
                    self.logger.info(self.log_prefix.format(
                        'The item is disabled to call.'))
                    self.log_prefix.pop()  # Scenario Stepping
                    continue
                self.log_prefix.pop()  # Scenario Stepping

                self.log_prefix.push('Operation Calling')
                data = self._call_item(item)
                self.logger.info(self.log_prefix.format(
                    'Done to run the item.'))
                self.logger.debug(StructureLogFormat(RESULT=data))
                self.log_prefix.push('Operation Result Handling')
                self._follow_up(data)
                self.log_prefix.pop()  # Operation Result Handling
                self.log_prefix.pop()  # Operation Calling

                time.sleep(0.001)

        except StopIteration:
            self.log_prefix.pop()  # Operation Stepping
        except ExceptionTreatAsError as e:
            with captured_output() as (out, _):
                traceback.print_exc()
            self.logger.error(self.log_prefix.format(out.getvalue()))
        except KeyboardInterrupt:
            self.logger.warn(self.log_prefix.format('Keyboard Interrupt.'))
        except Exception as e:
            with captured_output() as (out, _):
                traceback.print_exc()
            self.logger.error(self.log_prefix.format(out.getvalue()))
        finally:
            self.logger.info(self.log_prefix.format('The process has ended.'))
            self._run = False
            self.logger.debug(StructureLogFormat(PID=self.pid, RUN=self._run))
            self.log_prefix.pop()  # Runner
        return

    # ==========================================================================
    def init_variables(self):
        """
        변수매니져와 연결 및 변수 선언
        :return:
        """

        pid = os.getpid()
        try:
            self._variables = VariableManagerAPI(pid=pid, logger=self.logger)

            # 봇 필수 변수 선언
            self._variables.create('{{rp.index}}', value=1)  # Loop Index
            self._variables.create('{{saved_data}}', value=" ")  # Saved Data
            self.logger.info(self.log_prefix.format(
                "Declared Essential Variables."))

            # 사용자 변수 선언
            variable_list = self.scenario['userVariableList']
            for var in variable_list:
                variable = "{{%s.%s}}" % (var['GroupName'], var['VariableName'])
                self._variables.create(variable, None)
            self.logger.info(self.log_prefix.format(
                "Declared User Variables..."))
            ret = True
        except Exception as e:
            with captured_output() as (out, _):
                traceback.print_exc(file=out)
            self.logger.error(out.getvalue())
            ret = False
        finally:
            pass
        return ret

    # 아이템 실행결과에 따른 다음 동작
    # ResultHandler Scenario 관련
    # ==========================================================================
    def _result_handler_set_step(self, args):
        """
        STEP 변경
        * 모든 반복문은 초기화
        :param args:
        :return:
        """
        self.logger.info(self.log_prefix.format('ResultHandler: Set Step'))
        before = {"REPEAT_STACK": self.scenario._repeat_stack,
                  "STEP": self.scenario.step}

        self.scenario._repeat_stack = list()
        self.scenario.step = args[0]

        after = {"REPEAT_STACK": self.scenario._repeat_stack,
                 "STEP": self.scenario.step}
        self.logger.debug(StructureLogFormat(BEFORE=before, AFTER=after))

    # ==========================================================================
    def _result_handler_set_item(self, args):
        """
        다음 실행 오퍼레이터 변경
        * 모든 반복문은 초기화
        :param args:
        :return:
        """
        self.logger.info(self.log_prefix.format('Set Item'))
        before = {"REPEAT_STACK": self.scenario._repeat_stack,
                  "CUR_ITEM_INDEX": self.scenario.current_item_index}

        self.scenario._repeat_stack = list()
        self.scenario.set_current_item_by_index(int(args[0]))

        after = {"REPEAT_STACK": self.scenario._repeat_stack,
                 "CUR_ITEM_INDEX": self.scenario.current_item_index}

        self.logger.debug(StructureLogFormat(BEFORE=before, AFTER=after))

    # ==========================================================================
    def _result_handler_finish_step(self, args):
        """
        STEP 끝내기
        * 모든 반복문은 초기화
        :param args:
        :return:
        """
        self.logger.info(self.log_prefix.format('Finish Step'))
        before = {"REPEAT_STACK": self.scenario._repeat_stack,
                  "CUR_ITEM_INDEX": self.scenario.current_step_index}

        self.scenario._repeat_stack = list()
        self.scenario.next_step()

        after = {"REPEAT_STACK": self.scenario._repeat_stack,
                 "CUR_ITEM_INDEX": self.scenario.current_step_index}

        self.logger.debug(StructureLogFormat(BEFORE=before, AFTER=after))

    # ==========================================================================
    def _result_handler_jump_forward(self, args):
        self.logger.info(self.log_prefix.format('Jump Forward'))
        before = {"REPEAT_STACK": self.scenario._repeat_stack,
                  "CUR_ITEM_INDEX": self.scenario.current_item_index}

        self.scenario._repeat_stack = list()
        self.scenario.forward(int(args[0]))

        after = {"REPEAT_STACK": self.scenario._repeat_stack,
                 "CUR_ITEM_INDEX": self.scenario.current_item_index}

        self.logger.debug(StructureLogFormat(BEFORE=before, AFTER=after))

    # ==========================================================================
    def _result_handler_jump_backward(self, args):
        self.logger.info(self.log_prefix.format('Jump Backward'))
        before = {"REPEAT_STACK": self.scenario._repeat_stack,
                  "CUR_ITEM_INDEX": self.scenario.current_item_index}

        self.scenario._repeat_stack = list()
        self.scenario.backward(int(args[0]))

        after = {"REPEAT_STACK": self.scenario._repeat_stack,
                 "CUR_ITEM_INDEX": self.scenario.current_item_index}

        self.logger.debug(StructureLogFormat(BEFORE=before, AFTER=after))

    # ==========================================================================
    def _result_handler_finish_scenario(self, args):
        self.logger.info(self.log_prefix.format('Finish Scenario'))
        before = {"REPEAT_STACK": self.scenario._repeat_stack,
                  "CUR_ITEM_INDEX": self.scenario.current_item_index,
                  "CUR_STEP_INDEX": self.scenario.current_step_index,}

        self.scenario._repeat_stack = list()
        self.scenario.finish_scenario()

        after = {"REPEAT_STACK": self.scenario._repeat_stack,
                 "CUR_ITEM_INDEX": self.scenario.current_item_index,
                 "CUR_STEP_INDEX": self.scenario.current_step_index,}

        self.logger.debug(StructureLogFormat(BEFORE=before, AFTER=after))

    # ==========================================================================
    def _result_handler_goto(self, args):
        self.logger.info(self.log_prefix.format('ResultHandler: Goto'))
        before = {"REPEAT_STACK": self.scenario._repeat_stack,
                  "CUR_ITEM_INDEX": self.scenario.current_item_index,
                  "CUR_STEP_INDEX": self.scenario.current_step_index, }

        self.scenario._repeat_stack = list()
        self.scenario.step = int(args[0]) - 1
        self.scenario.set_current_item_by_index(int(args[1]) - 1)

        after = {"REPEAT_STACK": self.scenario._repeat_stack,
                 "CUR_ITEM_INDEX": self.scenario.current_item_index,
                 "CUR_STEP_INDEX": self.scenario.current_step_index, }

        self.logger.debug(StructureLogFormat(BEFORE=before, AFTER=after))

    # ResultHandler Variable 관련
    # ==========================================================================
    def _result_handler_set_variables(self, args):
        self.logger.info(self.log_prefix.format('ResultHandler: Set Variables'))

        for name, value in args:
            self._variables.create(name, value)

        self.logger.debug(StructureLogFormat(SET_VARIABLES=args))
