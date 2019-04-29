import codecs
import json
import pathlib
from alabs.pam.variable_manager.rc_api_variable_manager import \
    VariableManagerAPI

ITEM_DIVISION_TYPE = {
    "SystemCall": "systemCallType",
    "Event": "eventType",
    "Verification": "verifyType"}

################################################################################
class Scenario(dict):
    def __init__(self):
        dict.__init__(self)
        self.logger = None
        self._info = dict()
        # 현재 STEP과 ITEM INDEX
        # 절대 직접 접근하여 값을 바꾸지 말것
        self._current_step_index= 0
        self._current_item_index = 0

        # Repeat
        self._repeat_item = None

        # 변수 선언
        self._variables = None

        self._scenario_filename = ""
        # self.logger.info('>>>Start Initializing')

        self._scenario_image_dir = ""

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
        print(self.logger)
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
        self.init_variables()

    # ==========================================================================
    def init_variables(self):
        """
        변수매니져와 연결 및 변수 선언
        :return:
        """
        # self.logger.info('>>>Start Initializing variables')
        self._variables = VariableManagerAPI()

        # 봇 필수 변수 선언
        self._variables.create('{{rp.index}}', None)  # Loop Index
        self._variables.create('{{saved_data}}', None)  # Saved Data

        # 사용자 변수 선언
        variable_list = self['userVariableList']
        for var in variable_list:
            variable = "{{%s.%s}}" % (var['GroupName'], var['VariableName'])
            self._variables.create(variable, None)
        # self.logger.info('>>>End Initializing variables')

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
        class_name = data[ITEM_DIVISION_TYPE[data['itemDivisionType']]]
        _class = globals()[class_name]
        return _class(data, self)

    # ==========================================================================
    def __iter__(self):
        self._current_step_index = 0
        self._current_item_index = 0
        return self

    # ==========================================================================
    def __next__(self):
        if len(self.items) - 1 < self._current_item_index:
            # 시나리오 끝
            if len(self.steps) - 1 <= self._current_step_index:
                raise StopIteration
            # 다음 스텝이 있는 경우
            self._current_step_index += 1
            self._current_item_index = 0

        # 반복문 상태일 경우
        if isinstance(self._repeat_item, Repeat):
            item = self._repeat_item()
        else:
            item = self.item

        # 현재 정보 저장
        info = dict()
        info['scenario'] = self['name']
        info['step'] = "[{:d}] {}".format(
            self.current_step_index, self.step['name'])
        data = self.items[self._current_item_index]
        class_name = data[ITEM_DIVISION_TYPE[data['itemDivisionType']]]
        info['operator'] = "[{:d}] {} - {}".format(
            self.current_item_index,
            class_name,
            self.item['itemName'])
        self.info = info

        self._current_item_index += 1
        if isinstance(item, Repeat):
            self._repeat_item = item


        return item


    # ==========================================================================
    def set_current_item_by_index(self, index: int):
        """
        인덱스 번호로 현제 아이템 번호 설정
        :param index:
        :return:
        """
        if len(self.step) <= index:
            raise ValueError("Out of the index of the current step")
        self._current_item_index = index
        return self._current_item_index

    # ==========================================================================
    def get_item_by_id(self, _id):
        """
        아이템의 고유 아이디를 검색하여 찾은 아이템의 인덱스 번호를 리턴
        :param _id:
        :return:
        """
        for i, item in enumerate(self.items):
            if item['id'] == _id:
                return i
        return None




from alabs.pam.la.bot.operations import ExecuteProcess, Delay, SearchImage, \
    ImageMatch, MouseClick, MouseScroll, TypeKeys, TypeText, ReadImageText, \
    Repeat, SetVariable, StopProcess
