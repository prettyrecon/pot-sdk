import sys
import os
import time
import pathlib
import enum
import traceback
from collections import namedtuple
import multiprocessing as mp

from alabs.ppm import _main as ppm
from alabs.pam.runner import Runner
from alabs.pam.runner import is_timeout
from alabs.pam.scenario import Scenario
from alabs.common.util.vvlogger import get_logger, StructureLogFormat
from alabs.common.util.vvtest import captured_output
from contextlib import contextmanager
from io import StringIO
from alabs.pam.conf import get_conf
import site
# mp.set_start_method('spawn')


logger = get_logger(get_conf().get('/PATH/PAM_LOG'))


################################################################################
class PamManager(list):
    """
    PamManager는 PAM 생성, 관리를 목적으로 한다.
    리스트 아이템은 항상 RunnerInfo 타입을 사용
    """

    ############################################################################
    class RunnerData(enum.IntEnum):
        @classmethod
        def members(cls):
            return cls._member_names_
        RUNNER = 0
        PIPE = 1
        EVENT = 2

    RunnerInfo = namedtuple(
        'RunnerInfo', ' '.join(RunnerData.members()))

    ############################################################################
    def __init__(self, *args):
        list.__init__(self, *args)
        global logger
        self.logger = logger
        try:
            os.environ['PARENT_SITE'] = site.getsitepackages()[1]
        except AttributeError as e:
            os.environ['PARENT_SITE'] = os.path.dirname(site.__file__) + \
                                        '/site-packages'

    def __del__(self):
        if isinstance(self, PamManager):
            [proc.RUNNER.terminate() for proc in self if proc.RUNNER.is_alive()]
            [proc.RUNNER.join() for proc in self if proc.RUNNER.is_alive()]

    # Runner 시작 ##############################################################
    def start_runner(self, idx):
        self.logger.info("Runner Setting Start...")
        runner_info: PamManager.RunnerInfo() = self[idx]
        # 파이썬 인터프리터 지정
        if not runner_info.RUNNER.venv_python:
            self.logger.error(
                "VENV for scenario is not ready. Check the scenario file.")
            raise Exception

        # 멀티프레세스에서 사용하게 될 파이썬 지정
        mp.set_executable(runner_info.RUNNER.venv_python)
        self.logger.info("Set python executable path for the scenario.")
        self.logger.debug(
            StructureLogFormat(venv_python=str(runner_info.RUNNER.venv_python)))

        # 프로세스 생성
        if runner_info.RUNNER.is_alive():
            self.logger.error('Runner process is running already.')
            return False
        runner_info.RUNNER._debug_step_over = False
        runner_info.RUNNER._pause = False
        runner_info.RUNNER.start()
        runner_info.PIPE.send(runner_info.RUNNER.scenario_path)

        runner_info.PIPE.send(('play', ))

        # for _ in is_timeout(3):
        #     if runner_info.RUNNER.is_alive():
        #         return True
        return False

    # Runner 종료 ##############################################################
    @staticmethod
    def _create_runner():
        pipe_host, pipe_runner = mp.Pipe()  # 호스트와 러너의 통신용 파이프 생성
        event = mp.Event()  # 스위치
        runner = Runner(None, pipe_runner, event)

        return PamManager.RunnerInfo(runner, pipe_host, event)


    # Runner 에 Bot 설정 #######################################################
    def set_bot_to_runner(self, runner:RunnerInfo, scenario_path: str) -> bool:
        """
        PAM에 BOT을 설정
        :param runner_idx:
        :param scenario_path:
        :return:
        """
        try:
            # 러너에서 사용하게될 시나리오 파일 주소
            runner.RUNNER.scenario_path = scenario_path

            # PPM을 통해 venv 생성 또는 위치 구하기
            scenario = Scenario()
            scenario.load_scenario(scenario_path)
            self.logger.info('Scenario is loaded.')
            self.logger.debug(
                StructureLogFormat(SCENARIO_PATH=str(scenario_path)))

            # caution: alabs.ppm의 반환 값은 처리상태 값을 반환한다.
            # print() 를 통해서 원하는 결과 값이 반환되므로 stdout을 따로 캐치하여 사용
            # with captured_output() as (out, _):
            #     get_venv(scenario.plugins)
            # runner.RUNNER.venv_path = out.getvalue().strip()

            scenario.update(scenario.get_modules_list())
            with captured_output() as (out, _):
                get_venv(scenario.plugins)
            self.logger.debug(StructureLogFormat(VENV_PATH=out.getvalue()))
            out = out.getvalue().strip().split('\n')[-1]
            # out = out[:2] + out[3:]
            self.logger.debug(StructureLogFormat(VENV_PATH_EDITED=out))
            runner.RUNNER.venv_path = out

        except Exception as e:
            with captured_output() as (out, err):
                traceback.print_exc(file=out)
            self.logger.error(out.getvalue())
            self.logger.error(str(e))
            return False
        return True

    # 새로운 Runner 생성 ########################################################
    def create(self, scenario_path=None):
        """
        :param scenario_path:
        :return:
        """
        # 러너생성
        runner: PamManager.RunnerInfo = self._create_runner()

        if scenario_path:
            self.set_bot_to_runner(runner, scenario_path)
            # 시나리오 플러그인 목록에 맞는 파이썬 가상환경 생성
        self.insert(0, runner)
        return runner

    # Runner 에 Bot 설정 #######################################################
    def stop_runners(self, idx:list):
        """
        @startuml
        stop -> scenario
        @enduml
        :param idx:
        :return:
        """
        idx.sort()
        idx.reverse()
        for i in idx:
            self.stop_runner(i)

    def stop_runner(self, idx):
        """
        @startuml
        stop -> scenario
        @enduml
        :param idx:
        :return:
        """
        runner_info: PamManager.RunnerInfo() = self[idx]
        if not runner_info.RUNNER.is_alive():
            return True

        runner_info.RUNNER.kill()
        while is_timeout(3):
            if runner_info.RUNNER.exitcode:
                return True
            time.sleep(0.1)
        return False

    ############################################################################
    def get_runner(self, idx: int):
        return self[idx]

    ############################################################################
    def remove_runners(self, idx: list):
        idx.sort()
        idx.reverse()
        for i in idx:
            self.remove_runner(i)
        return True

    ############################################################################
    def remove_runner(self, idx):
        runner = self[idx]
        if runner.RUNNER.is_alive():
            return False
        del self[idx]
        return True

    #
    #
    #
    # mp.set_executable(pathlib.Path(
    #     "/Users/limdeokyu/Tests/Multiprocessing/venvs/v_1/bin/python"))
    #
    # # 정해진 수 만큼 프로세스를 생성
    # # PIPE를 생성하여 각 프로세스와 호스트를 연결
    # # 프로세스 리스트(processes)에 생성된 프로세스 추가
    # for name in PROCS:
    #     proc = namedtuple('pipe', 'proc host')
    #     queue, queue_runner = mp.Pipe()
    #     processes.append(proc(Runner(conn=pipe_runner, name=name), pipe_host))
    #     processes[-1].proc.start()
    #
    # # 타이머가 가진 시간(초)만큼 진행
    # # 각 프로세스는 자신이 필요로 하는 시간을 타이머에게 요청
    # timer = is_timeout(4)
    # for lt in timer:
    #     print(lt)
    #     # ----------------------------------------------------------------------
    #     # 모든 프로세스가 종료되었다면 타이머 잔여와 관계없이 탈출
    #     if not all([proc.proc.is_alive() for proc in processes]):
    #         print("ALL PROCESSES ARE DONE TO WORK")
    #         break
    #     # ----------------------------------------------------------------------
    #
    #     # 각 프로세스의 호스트 파이프라인 가져오기
    #     conns = [conn.host for conn in processes]
    #
    #     # 값 보내기
    #     if 0 == random.randrange(0, 10):
    #         processes[random.randrange(0, len(processes))]\
    #             .host.send(random.randrange(1, 5))
    #
    #     # 각 프로세스에서 전송해온 값이 있다면 타이머에 시간 추가
    #     data = mp.connection.wait(conns, timeout=0.1)
    #     if not data:
    #         continue
    #     for d in data:
    #         t = d.recv()
    #         timer.send(t)  # 시간 추가
    #         print("RECEIVED FROM {}: {}".format("main", t))
    #     time.sleep(0.1)
    #
    # # 프로세스 정리
    # [proc.proc.terminate() for proc in processes]
    # [proc.proc.join() for proc in processes]
    #
    # info("main", None)


################################################################################
# 파이썬 가상환경 생성, 가져오기
def get_venv(requirements):
    if not isinstance(requirements, (list, tuple)):
        raise TypeError
    # PPM에 가상환경 생성 요청
    # requirements = ['alabs.common==1.515.1543']
    essensial_modules = list()
    essensial_modules.append('alabs.common')
    # essensial_modules.append('pyautogui')
    # essensial_modules.append('bs4')
    if sys.platform == 'win32':
        pass
        # essensial_modules.append('opencv-python')
        # essensial_modules.append('opencv-contrib-python')

    essensial_modules += requirements
    req = ' '.join(essensial_modules)
    args = 'plugin venv {}'.format(req)
    logger.info('Installing plugins.')
    logger.debug(StructureLogFormat(PLUGINS=essensial_modules))
    cmd = 'python -m alabs.ppm {}'.format(args)
    import subprocess
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    # print(out.getvalue())
    out = out.read()
    err = err.read()
    # with captured_output() as (out, err):
    #     ppm(args.split())
    print(out)
    if err:
        logger.error(err)
        return False
    logger.info('Created python virtual environment.')
    logger.debug(StructureLogFormat(PATH=out))
    return True


if __name__ == "__main__":
    try:
        mgr = PamManager()
        SCENARIO_1 = pathlib.Path('alabs/pam/tests/scenarios/LA-Scenario0010/LA-Scenario0010.json')
            # './scenarios/LA-Scenario0010/LA-Scenario0010.json')

        mgr.create(str(SCENARIO_1))
        mgr.start_runner(0)
    except KeyboardInterrupt:
        pass
    finally:
        del mgr
