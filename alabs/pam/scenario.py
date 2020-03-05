import codecs
from alabs.common.util.vvlogger import get_logger, StructureLogFormat, \
    LogMessageHelper
from alabs.pam.operations import *
from alabs.pam.conf import get_conf

logger = get_logger(get_conf().get('/PATH/PAM_LOG'))

ITEM_DIVISION_TYPE = {
        "SystemCall": "systemCallType",
        "Event": "eventType",
        "Verification": "verifyType",
        "DebugReport": "debugReportType",
        "Plugin": "pluginType"}

VIRTUAL_ENV_PATH = None


################################################################################
class Scenario(dict):

    # ==========================================================================
    def __init__(self):
        dict.__init__(self)
        global logger
        self.logger = logger
        self.log_msg = LogMessageHelper()
        self._info = dict()

        # 현재 STEP과 ITEM Order 번호
        # 절대 직접 접근하여 값을 바꾸지 말것
        self._current_step_number = 0
        self._current_item_number = 0

        # Repeat
        self._repeat_stack = list()

        # 변수 선언
        self._variables = None

        self._scenario_filename = ""
        self._scenario_image_dir = ""
        self.is_skip = False

        # Web Driver
        self.web_driver = None

    # ==========================================================================
    @property
    def name(self):
        return self.setdefault('name', '')

    @property
    def description(self):
        return self.setdefault('description', '')

    # 암호·복호화 관련 프로퍼티 ==================================================
    @property
    def hash_key(self):
        return self['hashKey']

    @property
    def iv(self):
        return "2RmmGyA4M63oKxmOV3pzoA=="

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
    # def set_logger(self, logger):
    #     self.logger = logger

    # ==========================================================================
    def load_scenario(self, scn_filename):
        self._scenario_filename = scn_filename

        # 시나리오 불러오기
        self.update(self.load_scenario_file(scn_filename))
        self._scenario_image_dir = str(pathlib.Path(scn_filename).parent)
        self.logger.debug(
            StructureLogFormat(SCN_IMAGE_DIR=self._scenario_image_dir))

    # ==========================================================================
    def get_modules_list(self):
        ret = dict()
        ret['pluginVersion'] = list()
        # ret['pluginVersion'].append(
        #     {"name": "alabs.common", "version": "1.515.1543"})
        for step in self['stepList']:
            for item in step['items']:
                if item['itemDivisionType'] != 'Plugin':
                    continue
                dumpspec = json.loads(item['pluginDumpspec'])
                ret['pluginVersion'].append(
                    # {"name": item['pluginType'],
                    {"name": item['pluginType'][3:] if item['pluginType'][0] == '(' else item['pluginType'] ,
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
        global logger
        with codecs.open(filename, 'r', 'utf-8-sig') as f:
            try:
                scn = json.load(f)
            except Exception as e:
                logger.error(str(e))
                raise TypeError('The Scenario`s json File is Something Wrong')
            finally:
                logger.debug(StructureLogFormat(SCN_FILE_PATH=str(filename)))
        return scn

    # ==========================================================================
    @property
    def current_step_index(self)->int:
        return self._current_step_number

    # ==========================================================================
    @property
    def current_item_index(self) -> int:
        return self._current_item_number

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
        return self.steps[self._current_step_number]

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
            self.logger.error(self.log_msg.format(
                'Out of the step order number'))
            raise ValueError('Out of the step order number')
        self._current_step_number = order
        self._current_item_number = 0

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
        self.logger.info(self.log_msg.format('Making a item instance.'))
        data = self.items[self._current_item_number]
        class_name = data[ITEM_DIVISION_TYPE[data['itemDivisionType']]]
        # 플러그인 타입의 class_name은 플러그인 이름이 적혀있음
        if 'pluginType' == ITEM_DIVISION_TYPE[data['itemDivisionType']]:
            class_name = 'Plugin'
        _class = globals()[class_name]
        item = _class(data, self, logger=self.logger)
        return item

    # ==========================================================================
    @item.setter
    def item(self, index):
        """
        현재 스탭에서 아이템 인덱스 값으로 검색하여 현재 아이템 설정
        :param index:
        :return:
        """
        for i, item in enumerate(self.items):
            if item['index'] == index:
                self._current_item_number = i
        raise ValueError('There is not the index of the item.')

    # ==========================================================================
    def __iter__(self):
        self._current_step_number = 0
        self._current_item_number = 0
        return self

    # ==========================================================================
    def _get_current_info(self):
        """
        현재 시나리오 정보
        :return:
        """
        # 현재 정보 저장
        info = dict()

        info['scenario'] = {
            'name': self['name']}

        info['step'] = {
            'order': self.current_step_index,
            'name': self.step['name']}

        # data = self.items[self._current_item_number]
        # class_name = data[ITEM_DIVISION_TYPE[data['itemDivisionType']]]
        info['operator'] = {
            'order': self.current_item_index,
            'name': self.item['itemName']}
        return info

    # ==========================================================================
    def __next__(self):
        # 반복문 스택 존재 검사
        if self._repeat_stack:
            self.logger.info(self.log_msg.format('Working in the loop action.'))
            self.logger.debug(
                StructureLogFormat(REPEAT_STACK=self._repeat_stack))
            self._current_item_number = self._repeat_stack[-1].get_next()

        if len(self.items) - 1 < self._current_item_number:
            # 시나리오 끝
            if len(self.steps) - 1 <= self._current_step_number:
                self.logger.info(self.log_msg.format(
                    'Reached at the end of the scenario.'))
                raise StopIteration
            # 다음 스텝이 있는 경우
            self.logger.info(self.log_msg.format(
                'Reached at the end of the step.'))
            self._current_step_number += 1
            self._current_item_number = 0

        item = self.item

        self.info = self._get_current_info()

        self._current_item_number += 1
        return item

    # ==========================================================================
    def set_current_item_by_index(self, index: int):
        """
        인덱스 번호로 현제 아이템 번호 설정
        오더번호임
        :param index:
        :return:
        """
        for i, item in enumerate(self.items):
            if item['index'] == index:
                self._current_item_number = i
                return self._current_item_number
        raise ValueError('There is not the index of the item.')

    # ==========================================================================
    def set_current_item_by_order(self, order: int):
        if len(self.items) <= order:
            self.logger.error(self.log_msg.format(
                "Out of the order of the current step"))
            raise ValueError("Out of the order of the current step")
        self._current_item_number = order


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
        quotient = self._current_item_number - n
        # 아이템의 첫번째를 벗어나는 경우, 이전 스텝으로 이동
        if quotient < 0:
            if self._current_step_number == 0:
                self.logger.error(self.log_msg.format(
                    "Out of the index of the current step"))
                raise IndexError
            self._current_step_number -= 1
            self._current_item_number = (len(self.items) - 1) - quotient
        else:
            self._current_item_number -= n

    # ==========================================================================
    def next_step(self):
        self.set_current_item_by_order(len(self.items) - 1)
        next(self)

    # ==========================================================================
    def finish_scenario(self):
        raise StopIteration

        # self.set_step_by_index(len(self.steps) - 1)
        # self.set_current_item_by_index(len(self.items) - 1)
        # next(self)






