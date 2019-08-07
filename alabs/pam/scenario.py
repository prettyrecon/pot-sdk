import codecs
import json
from alabs.common.util.vvlogger import get_logger

from alabs.pam.operations import *
# from alabs.pam.operations import ExecuteProcess


################################################################################
class Scenario(dict):
    ITEM_DIVISION_TYPE = {
        "SystemCall": "systemCallType",
        "Event": "eventType",
        "Verification": "verifyType",
        "DebugReport": "debugReportType",
        "Plugin": "pluginType"}
    VIRTUAL_ENV_PATH = None

    # ==========================================================================
    def __init__(self):
        dict.__init__(self)
        self.logger = get_logger(os.environ.setdefault('PAM_LOG', 'runner.log'))
        self._info = dict()
        # 현재 STEP과 ITEM INDEX
        # 절대 직접 접근하여 값을 바꾸지 말것
        self._current_step_index = 0
        self._current_item_index = 0

        # Repeat
        self._repeat_stack = list()

        # 변수 선언
        self._variables = None

        self._scenario_filename = ""
        # self.logger.info('>>>Start Initializing')

        self._scenario_image_dir = ""
        self.is_skip = False

    # ==========================================================================
    @property
    def name(self):
        return self.setdefault('name', '')

    @property
    def description(self):
        return self.setdefault('description', '')

    # 사용된 의존 플러그인 프로퍼티 ==============================================
    @property
    def plugins(self):
        # {'name': 'alabs.common', 'version': '1.515.1543'}
        # ['alabs.common==1.515.1543']
        plugins = self.setdefault('pluginVersion', [])
        return ["{name}=={version}".format(**d) for d in plugins]
    # ==========================================================================
    @property
    def info(self):
        return self._info
    @info.setter
    def info(self, v):
        self._info.update(v)

    # ==========================================================================
    def set_logger(self, logger):
        self.logger = logger
        self.logger.info('>>>Set the logger')

    # ==========================================================================
    def load_scenario(self, scn_filename):
        self._scenario_filename = scn_filename

        # 시나리오 불러오기
        self.logger.info('>>>Start Loading the scenario file...{filename}' \
                         .format(filename=scn_filename))
        self.update(self.load_scenario_file(scn_filename))
        self.logger.info('>>>End Loading the scenario file...{filename}'.format(
            filename=scn_filename))

        self._scenario_image_dir = str(pathlib.Path(scn_filename).parent)
        self.update(self.get_modules_list())

    # ==========================================================================
    def get_modules_list(self):
        ret = dict()
        ret['pluginVersion'] = list()
        ret['pluginVersion'].append(
            {"name": "alabs.common", "version": "1.515.1543"})
        for step in self['stepList']:
            for item in step['items']:
                if item['itemDivisionType'] != 'Plugin':
                    continue
                dumpspec = json.loads(item['pluginDumpspec'])
                ret['pluginVersion'].append(
                    {"name": item['pluginType'],
                     'version': dumpspec['plugin_version']})
        return ret





    # ==========================================================================
    @staticmethod
    def load_scenario_file(filename):
        """
        Scenario File (Json)을 불러오기
        :param filename:
        :return:
        """
        scn = None
        with codecs.open(filename, 'r', 'utf-8-sig') as f:
            try:
                scn = json.load(f)
            except Exception as e:
                raise TypeError('The Scenario File is Something Wrong')

        return scn

    # ==========================================================================
    @property
    def current_step_index(self)->int:
        return self._current_step_index

    # ==========================================================================
    @property
    def current_item_index(self) -> int:
        return self._current_item_index

    # ==========================================================================
    @property
    def steps(self)->list:
        return self['stepList']

    # ==========================================================================
    @property
    def step(self):
        """
        return current step
        :return:
        """
        return self.steps[self._current_step_index]

    # ==========================================================================
    @step.setter
    def step(self, order: int):
        """
        주의: Order 번호와 Index는 다르다.
        스텝 값을 입력 받음
        :param index:
        :return:
        """
        if len(self.steps) < order + 1:
            self.logger.error('Out of the step order number')
            raise ValueError('Out of the step order number')
        self._current_step_index = order
        self._current_item_index = 0

    # ==========================================================================
    def set_step_by_index(self, index: int):
        """
        주의: LA JSON 파일의 스텝 인덱스
        찾고자 하는 스탭 index를 받아서 시나리오안의 모든 스탭을 검사한 뒤, 설정
        :param index:
        :return: 현재 설정된 스텝 Order 번호
        """
        for i, step in enumerate(self.steps):
            if step['index'] == index:
                self.step = i
                return i
        raise ValueError('There is not the step.')

    # ==========================================================================
    @property
    def items(self) -> list:
        """
        현재 스탭의 아이탬을 반환
        :return:
        """
        return self.step['items']

    # ==========================================================================
    @property
    def item(self):
        data = self.items[self._current_item_index]
        class_name = data[self.ITEM_DIVISION_TYPE[data['itemDivisionType']]]
        # 플러그인 타입의 class_name은 플러그인 이름이 적혀있음
        if 'pluginType' == self.ITEM_DIVISION_TYPE[data['itemDivisionType']]:
            class_name = 'Plugin'
        _class = globals()[class_name]
        item = _class(data, self, logger=self.logger)
        return item

    # ==========================================================================
    def __iter__(self):
        self._current_step_index = 0
        self._current_item_index = 0
        return self

    # ==========================================================================
    def __next__(self):
        # 반복문 스택 존재 검사
        if self._repeat_stack:
            self._current_item_index = self._repeat_stack[-1].get_next()

        if len(self.items) - 1 < self._current_item_index:
            # 시나리오 끝
            if len(self.steps) - 1 <= self._current_step_index:
                raise StopIteration
            # 다음 스텝이 있는 경우
            self._current_step_index += 1
            self._current_item_index = 0

        item = self.item

        # 현재 정보 저장
        # info = dict()
        # info['scenario'] = self['name']
        # info['step'] = "[{:d}] {}".format(
        #     self.current_step_index, self.step['name'])
        # data = self.items[self._current_item_index]
        # class_name = data[self.ITEM_DIVISION_TYPE[data['itemDivisionType']]]
        # info['operator'] = "[{:d}] {} - {}".format(
        #     self.current_item_index,
        #     class_name,
        #     self.item['itemName'])
        # self.info = info

        self._current_item_index += 1
        return item

    # ==========================================================================
    def set_current_item_by_index(self, index: int):
        """
        인덱스 번호로 현제 아이템 번호 설정
        오더번호임
        :param index:
        :return:
        """
        if len(self.step) <= index:
            raise ValueError("Out of the index of the current step")
        self._current_item_index = index
        return self._current_item_index

    # ==========================================================================
    def get_item_order_number_by_index(self, _id):
        """
        아이템의 인덱를 검색하여 찾은 아이템의 오더 번호를 리턴
        :param _id:
        :return:
        """
        for i, item in enumerate(self.items):
            if item['index'] == _id:
                return item['order']
        return None

    # ==========================================================================
    def forward(self, n: int):
        for _ in range(n):
            next(self)

    # ==========================================================================
    def backward(self, n: int):
        quotient = self._current_item_index - n
        # 아이템의 첫번째를 벗어나는 경우, 이전 스텝으로 이동
        if quotient < 0:
            if self._current_step_index == 0:
                raise IndexError
            self._current_step_index -= 1
            self._current_item_index = (len(self.items) - 1) - quotient
        else:
            self._current_item_index -= n

    # ==========================================================================
    def next_step(self):
        self.set_current_item_by_index(len(self.items) - 1)
        next(self)
        next(self)

    # ==========================================================================
    def finish_scenario(self):
        self.set_step_by_index(len(self.steps) - 1)
        self.set_current_item_by_index(len(self.items) - 1)
        next(self)






