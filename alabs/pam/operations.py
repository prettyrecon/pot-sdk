import pathlib
import enum
import subprocess
import os
import json
import csv
import locale

from io import StringIO
from functools import wraps

from alabs.pam.dumpspec_parser import plugin_spec_parser
from alabs.pam.variable_manager.rc_api_variable_manager import \
    VariableManagerAPI
from alabs.common.util.vvtest import captured_output
from alabs.common.util.vvlogger import StructureLogFormat, LogMessageHelper
from alabs.pam.conf import get_conf


################################################################################
ITEM_DIVISION_TYPE = {
    "SystemCall": "systemCallType",
    "Event": "eventType",
    "Verification": "verifyType",
    "Plugin": "pluginType"}


################################################################################
class ClickMotionType(enum.Enum):
    CLICK = 'DownAndUP'
    PRESS = 'Down'
    RELEASE = 'Up'


################################################################################
class ClickType(enum.Enum):
    RIGHT = 'Right'
    LEFT = 'Left'
    DOUBLE = 'Double'
    NONE = 'None'


################################################################################
def get_image_path(path):
    path = pathlib.Path(path)
    scenario_filename = pathlib.Path(path.parts[-1])
    images = pathlib.Path('Images')
    # root_path = pathlib.Path('/Users/limdeokyu/naswork/raven/Work/argos-rpa/alabs-common/alabs/pam/la/bot/tests/scenarios/MacOS/LA-Scenario0010/Images/LA-Scenario0010.json')
    path = path.parent / images / scenario_filename
    return str(path)


################################################################################
def separate_coord(coord:str)->tuple:
    return tuple(coord.replace(' ', '').split(','))


################################################################################
def arguments_options_fileout(f):
    @wraps(f)
    def func(*args, **kwargs):
        arguments = list(f(*args, **kwargs))
        stdout = get_conf().get('/PATH/OPERATION_STDOUT_FILE')
        if stdout:
            arguments += ['--outfile ', stdout]
        log = get_conf().get('/PATH/OPERATION_LOG')
        stderr = get_conf().get('/PATH/OPERATION_STDERR_FILE')

        if log:
            arguments += ['--errfile ', stderr]
            arguments += ['--logfile', log]
        return tuple(arguments)
    return func


################################################################################
def request_handler(f):
    @wraps(f)
    def func(*args, **kwargs):
        from alabs.pam.runner import ResultHandler, ResultAction
        action = dict((x.value, x.name) for x in list(ResultAction))
        result_data, result, message = f(*args, **kwargs)

        status = True
        function = None
        message = ''

        if action[result] == ResultAction.MoveOn.value:
            pass
        elif action[result] == ResultAction.TreatAsError.value:
            status = False
            message = message
        elif action[result] == ResultAction.IgnoreFailure.value:
            function = (ResultHandler.SCENARIO_FINISH_STEP.value, None)
        elif action[result] == ResultAction.AbortScenarioButNoError.value:
            function = (ResultHandler.SCENARIO_FINISH_SCENARIO.value, None)
        else:
            pass
        return make_follow_job_request(status, function, message)
    return func

################################################################################
def make_follow_job_request(status, function=None, message=''):
    """

    :param status: Bool
    :param function: Tuple(name, args)
    :return:
    """
    data = dict()
    if not isinstance(status, bool):
        raise TypeError
    data['status'] = status
    data['function'] = function
    data['message'] = message
    return data


################################################################################
class Items(dict):
    class Type(enum.Enum):
        EXECUTABLE_ITEM = 0
        LOGIC_ITEM = 1
        SYSTEM_ITEM = 2

    item_ref = ("id", "index", "itemName", "timeOut", "order",
                "beforeDelayTime", "Disabled")

    references = tuple()
    item_type = None

    def __init__(self, data:dict, scenario, logger=None):
        dict.__init__(self)
        self.logger = logger
        self.log_msg = LogMessageHelper()
        self._scenario = scenario
        t = dict()
        t['ITEM'] = dict()
        for r in self.item_ref:
            self[r] = data[r]
            t['ITEM'][r] = data[r]
        t['REFERENCE'] = dict()
        for r in self.references:
            self[r] = data.setdefault(r, None)
            t['REFERENCE'][r] = data.setdefault(r, None)
        self.logger.debug(StructureLogFormat(DATA=t))

        self._variables = VariableManagerAPI(pid=str(os.getpid()),
                                             logger=logger)
        self.locale = locale.getdefaultlocale()[1]

    # ==========================================================================
    def __call__(self):
        raise NotImplementedError

    # ==========================================================================
    @property
    def data(self):
        return self


################################################################################
class ExecuteProcess(Items):
    item_type = Items.Type.EXECUTABLE_ITEM
    references = ('executeProcess',)
    # {'executeProcess': {
    #     'executeFilePath': '"C:\\Program Files (x86)\\Google\\Chrome'
    #                        '\\Application\\chrome.exe" -kiosk -fullscreen'
    #                        ' http://192.168.99.250/scenarios/LA-Scenario0010'
    #                        '/00_locateimage.html'}}

    # ==========================================================================
    @property
    # @arguments_options_fileout
    def arguments(self)-> tuple:
        code, data = self._variables.convert(
            self['executeProcess']['executeFilePath'])
        if code != 200:
            raise ValueError(str(data))
        return data,

    # ==========================================================================
    def __call__(self):
        self.log_msg.push('Execute Process')
        cmd = 'python -m alabs.rpa.desktop.execute_process {}'.format(
            ' '.join(self.arguments))
        self.logger.info(self.log_msg.format('Calling...'))
        self.logger.debug(StructureLogFormat(COMMAND=cmd))
        subprocess.Popen(self.arguments)
        # os.system(' '.join(self.arguments))
        # subprocess.Popen(self.arguments, shell=True)
        # subprocess.Popen(cmd, shell=True)
        # subprocess.call(cmd, shell=True)
        self.log_msg.pop()
        return make_follow_job_request(True, None, '')


################################################################################
class Delay(Items):
    item_type = Items.Type.EXECUTABLE_ITEM
    references = ('delay',)
    # {'delay': {'delay': '4000'}}

    # ==========================================================================
    @property
    @arguments_options_fileout
    def arguments(self)->tuple:
        return self['delay']['delay'],

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        self.log_msg.push('Delay')
        cmd = 'python -m alabs.rpa.desktop.delay {}'.format(
            ' '.join(self.arguments))
        self.logger.info(self.log_msg.format('Calling...'))
        self.logger.debug(StructureLogFormat(COMMAND=cmd))

        with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE) as proc:
            stdout = proc.stdout.read()
        self.log_msg.pop()
        return make_follow_job_request(True, None, '')


################################################################################
class SearchImage(Items):
    # LocateImage
    item_type = Items.Type.EXECUTABLE_ITEM
    references = ('imageMatch',)
    # {'imageMatch': {'clickType': 'Left', 'clickMotionType': 'DownAndUP',
    #                 'cropImageLocation': '330, 115, 330, 452',
    #                 'searchLocation': '0, 0, 1650, 1080',
    #                 'ocrLocation': '0, 0, 0, 0', 'clickPoint': '185, 306',
    #                 'cropImageFileName': 'temp_636804995577879195_e41e233fee2b4f899816bddff419e255_2_CropImage.png',
    #                 'cropImageFileChecksum': 'B4B024F0BA0E6B4FA4D3515C333D2E4D',
    #                 'ocrImageFileName': None, 'ocrImageFileChecksum': None,
    #                 'similarity': '50', 'highLow': 'High', 'isShownAdv': False,
    #                 'highLowDS': 'Above', 'title': 'Title - Google Chrome',
    #                 'processName': 'chrome', 'ocrOptionName': None,
    #                 'ocrFilterOptionToString': None, 'ocrReadTextFormat': None,
    #                 'ocrLib': None, 'ocrLang': None, 'text': None,
    #                 'imageIndex': '0', 'classPath': None}}

    # ==========================================================================
    @property
    @arguments_options_fileout
    def arguments(self) -> tuple:
        cmd = list()
        # filename
        parent = pathlib.Path(self._scenario._scenario_image_dir)
        filename = get_image_path(self._scenario._scenario_filename) + '/' + \
                   self['imageMatch']['cropImageFileName']
        cmd.append(filename)
        # cmd.append(parent / pathlib.Path(self['imageMatch']['cropImageFileName']))
        # cmd.append(get_image_path(self['imageMatch']['cropImageFileName']))

        # region
        cmd.append('--region')
        cmd += separate_coord(self['imageMatch']['cropImageLocation'])

        # coordinates
        cmd.append('--coordinates')
        cmd += separate_coord(self['imageMatch']['clickPoint'])
        # button
        b = self['imageMatch']['clickType']
        b = vars(ClickType)['_value2member_map_'][b].name

        # motion
        m = self['imageMatch']['clickMotionType']
        m = vars(ClickMotionType)['_value2member_map_'][m].name

        if b == ClickType['DOUBLE'].name:
            m = ClickType['DOUBLE'].name
            b = ClickType['LEFT'].name

        cmd.append('--button')
        cmd.append(b)

        cmd.append('--motion')
        cmd.append(m)
        return tuple(cmd)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        self.log_msg.push('Locate Image')
        cmd = 'python -m alabs.rpa.autogui.locate_image {}'.format(
            ' '.join(self.arguments))
        self.logger.info(self.log_msg.format('Calling...'))
        self.logger.debug(StructureLogFormat(COMMAND=cmd))

        with subprocess.Popen(cmd, shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as proc:
            stdout = proc.stdout.read()
            stderr = proc.stderr.read()
        if stderr:
            self.logger.error(stderr)
        self.log_msg.pop()
        # return locate_image(*self.arguments)


################################################################################
class ImageMatch(Items):
    item_type = Items.Type.EXECUTABLE_ITEM
    references = ('imageMatch', 'verifyResultAction')
    # {'imageMatch': {'clickType': 'Left', 'clickMotionType': 'DownAndUP',
    #                 'cropImageLocation': '6, 19, 277, 43',
    #                 'searchLocation': '0, 0, 1114, 191',
    #                 'ocrLocation': '0, 0, 0, 0', 'clickPoint': '0, 0',
    #                 'cropImageFileName': 'temp_636804995577879195_7c0985b2ebe14a39b29dbefef8726267_1_CropImage.png',
    #                 'cropImageFileChecksum': '0D49C74F4689615F021B50483F8994AE',
    #                 'ocrImageFileName': None, 'ocrImageFileChecksum': None,
    #                 'similarity': '70', 'highLow': 'High', 'isShownAdv': False,
    #                 'highLowDS': 'Above', 'title': 'Title - Google Chrome',
    #                 'processName': 'chrome', 'ocrOptionName': None,
    #                 'ocrFilterOptionToString': None, 'ocrReadTextFormat': None,
    #                 'ocrLib': None, 'ocrLang': None, 'text': '',
    #                 'imageIndex': '0', 'classPath': None},
    #  'verifyResultAction': {'successActionType': 'Go', 'successActionValue': 0,
    #                         'successFilterMemo': None,
    #                         'successMemoGroupCode': 0,
    #                         'successActionRepeatCount': 5,
    #                         'failActionType': 'Error', 'failActionValue': 0,
    #                         'failFilterMemo': None, 'failMemoGroupCode': 0,
    #                         'failActionRepeatCount': 5}}

    # ==========================================================================
    @property
    @arguments_options_fileout
    def arguments(self) -> tuple:
        cmd = list()
        # filename
        filename = get_image_path(self._scenario._scenario_filename) + '/' + \
                   self['imageMatch']['cropImageFileName']
        cmd.append(filename)

        # region
        cmd.append('--region')
        cmd += separate_coord(self['imageMatch']['cropImageLocation'])
        return tuple(cmd)

    # ==========================================================================
    @request_handler
    def __call__(self, *args, **kwargs):
        self.log_msg.push('Find Image')
        cmd = 'python -m alabs.rpa.autogui.find_image_location {}'.format(
            ' '.join(self.arguments))
        self.logger.info(self.log_msg.format('Calling...'))
        self.logger.debug(StructureLogFormat(COMMAND=cmd))

        with subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True) as proc:
            stdout = proc.stdout.read()
            stderr = proc.stderr.read()
            returncode = proc.returncode

        if stderr:
            message = stderr.decode()
            self.logger.error(self.log_msg.format(message))
            return self['verifyResultAction'], \
                   self['verifyResultAction']['failActionType'], \
                   message

        message = stdout.decode()
        self.log_msg.pop()
        return self['verifyResultAction'], \
               self['verifyResultAction']['successActionType'], \
               message

        # stdout = b'10, 3'
        # act = stdout.decode().split(',')[1]



################################################################################
class MouseScroll(Items):
    item_type = Items.Type.EXECUTABLE_ITEM
    references = ('mouseScroll',)
    # 'mouseScroll': {'scrollX': '0', 'scrollY': '0', 'scrollLines': '40'}
    # ==========================================================================
    @property
    @arguments_options_fileout
    def arguments(self) -> tuple:
        v = int(self['mouseScroll']['scrollLines'])
        return '--vertical', v

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        self.log_msg.push('Scroll')
        cmd = 'python -m alabs.rpa.autogui.scroll {}'.format(
            ' '.join([str(x) for x in self.arguments]))
        self.logger.info(self.log_msg.format('MouseScrolling Calling...'))
        self.logger.debug(StructureLogFormat(COMMAND=cmd))

        subprocess.Popen(cmd, shell=True)
        # return scroll(*self.arguments)
        self.log_msg.pop()


################################################################################
class MouseClick(Items):
    item_type = Items.Type.EXECUTABLE_ITEM
    references = ('mouseClick',)
    # 'mouseClick': {'baseAreaType': 'FullScreen', 'clickType': 'Left',
    #                'clickMotionType': 'DownAndUP', 'clickPoint': '147, 649',
    #                'frameName': None, 'tagName': None, 'attName': None,
    #                'attValue': None, 'appName': '', 'title': '',
    #                'IsActivvateWindow': False, 'classPath': None},
    # ==========================================================================
    @property
    @arguments_options_fileout
    def arguments(self) -> tuple:
        cmd = list()
        # coordinates
        cmd += separate_coord(self['mouseClick']['clickPoint'])

        # button
        b = self['mouseClick']['clickType']
        b = vars(ClickType)['_value2member_map_'][b].name

        # motion
        m = self['mouseClick']['clickMotionType']
        m = vars(ClickMotionType)['_value2member_map_'][m].name

        if b == ClickType['DOUBLE'].name:
            m = ClickType['DOUBLE'].name
            b = ClickType['LEFT'].name

        cmd.append('--button')
        cmd.append(b)

        cmd.append('--motion')
        cmd.append(m)
        return tuple(cmd)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        self.log_msg.push('Click')
        cmd = 'python -m alabs.rpa.autogui.click {}'.format(
            ' '.join(self.arguments))
        self.logger.info(self.log_msg.format('Calling...'))
        self.logger.debug(StructureLogFormat(COMMAND=cmd))

        with subprocess.Popen(cmd, shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as proc:
            stdout = proc.stdout.read()
            stderr = proc.stderr.read()
        if stderr:
            self.logger.error(self.log_msg.format(stderr.decode(self.locale)))
        self.log_msg.pop()



################################################################################
class TypeText(Items):
    item_type = Items.Type.EXECUTABLE_ITEM
    references = ('typeText',)
    # 'typeText': {'typeTextType': 'Text', 'keyValue': 'ArgosLabs',
    #              'variableName': None, 'variableCode': None,
    #              'userVariableGroup': None, 'userVariableName': None,
    #              'userVariableIsArray': False, 'useVirtualKeyboard': False,
    #              'useSecurityCard': False, 'securityCardLeftSide': False}

    # ==========================================================================
    @property
    @arguments_options_fileout
    def arguments(self) -> tuple:
        _type = self['typeText']['typeTextType']
        if "Text" == _type:
            # TODO: 없는 자료일 경우 처리
            code, data = self._variables.convert(self['typeText']['keyValue'])
            value = data
        elif "UserVariable" == _type:
            # TODO: 없는 자료일 경우 처리
            variable_name = "{{%s.%s}}" % (
                self['typeText']['userVariableGroup'],
                self['typeText']['userVariableName'])
            code, value = self._variables.get(variable_name)
        else:
            # TODO: 없는 자료일 경우 처리
            # Saved Data
            code, value = self._variables.get("{{saved_data}}")
            # raise ValueError("Not Supported Yet")
        # 리눅스 Bash에서 해당 문자열은 멀티라인을 뜻하므로 이스케이프문자 처리
        value = value.replace('`', '\`')
        return tuple([json.dumps(value),])

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        self.log_msg.push('Type Text')
        cmd = 'python -m alabs.rpa.autogui.type_text {}'.format(
            ' '.join(self.arguments))
        self.logger.info(self.log_msg.format('TypeText Calling...'))
        self.logger.debug(StructureLogFormat(COMMAND=cmd))

        subprocess.check_call(cmd, shell=True)
        self.log_msg.pop()
        return make_follow_job_request(True, None, '')


################################################################################
class TypeKeys(Items):
    item_type = Items.Type.EXECUTABLE_ITEM
    references = ('keycodes',)
    # 'keycodes': [
    #     {'txt': '[Enter]', 'lcontrol': False, 'lalt': False, 'lshift': False,
    #      'rcontrol': False, 'ralt': False, 'rshift': False, 'lWin': False,
    #      'rWin': False, 'keyCode': 13, 'duration': 10, 'interval': 500,
    #      'isDelete': False, 'durationDS': 0.01, 'intervalDS': 0.5}]

    # ==========================================================================
    @property
    def arguments(self) -> tuple:
        value = list()
        for k in self['keycodes']:
            value.append(('--txt', json.dumps(k['txt'])))
        res = list()
        for d in value:
            res.append(self.add_options(d))
        return tuple(res)

    @arguments_options_fileout
    def add_options(self, arg):
        return tuple(arg)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        self.log_msg.push('Send Shortcut')
        for arg in self.arguments:
            self.logger.info(self.log_msg.format('Calling...'))
            cmd = 'python -m alabs.rpa.autogui.send_shortcut {}'.format(
                ' '.join(arg))
            self.logger.debug(StructureLogFormat(COMMAND=cmd))
            subprocess.check_call(cmd, shell=True)
        self.log_msg.pop()
        return make_follow_job_request(True, None, '')


################################################################################
class StopProcess(Items):
    references = ('stopProcess',)
    # "stopProcess": {"processName": "notepad"}
    # ==========================================================================
    @property
    def arguments(self) -> tuple:
        res = list()
        res.append('--process_name')
        res.append(self['stopProcess']['processName'])
        return tuple(res)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        self.log_msg.push('Stop Process')
        cmd = 'python -m alabs.rpa.desktop.stop_process {}'.format(
            ' '.join(self.arguments))
        self.logger.info(self.log_msg.format('Calling...'))
        self.logger.debug(StructureLogFormat(COMMAND=cmd))

        subprocess.check_call(cmd, shell=True)
        self.log_msg.pop()
        return make_follow_job_request(True, None, '')

################################################################################
class ReadImageText(Items):
    # OCR
    references = ('imageMatch',)

    # ==========================================================================
    @property
    def arguments(self) -> tuple:
        return tuple()

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        return


################################################################################
class SelectWindow(Items):
    # OCR
    references = ('imageMatch',)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        return


################################################################################
class HtmlAction(Items):
    # OCR
    references = ('imageMatch',)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        return


################################################################################
class BrowserScript(Items):
    # OCR
    references = ('imageMatch',)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        return


################################################################################
class ReadImage(Items):
    # OCR
    references = ('imageMatch',)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        return

################################################################################
class Goto(Items):
    references = ('gotoAction',)
    # "gotoAction":{
    #   "stepDisplayName":"1","itemDisplayName":"[1] Operation 1",
    #   "stepNum":1,"itemNum":1},

    # ==========================================================================
    @property
    def arguments(self):
        return self['gotoAction']['stepNum'], self['gotoAction']['itemNum']

    # ==========================================================================
    def __call__(self):
        self.log_msg.push('Goto')
        from alabs.pam.runner import ResultHandler
        self.logger.info(self.log_msg.format('Calling...'))
        self.logger.debug(StructureLogFormat(STEP_ITEM=self.arguments))
        function = (ResultHandler.SCENARIO_GOTO.value, self.arguments)
        self.log_msg.pop()
        return make_follow_job_request(True, function, '')


################################################################################
class Repeat(Items):
    """
    @startuml
    Runner ->
    @enduml
    """
    references = ('repeat',)

    # ==========================================================================
    def __init__(self, data:dict, scenario, logger):
        Items.__init__(self, data, scenario, logger)
        self._variables.create("{{rp.index}}", self.start_index)
        self._start_item_order = self._scenario.current_item_index + 1
        self._scenario._repeat_stack.append(self)
        self._status = True
        self._times = self.repeat_times
        self.logger.info(self._times)
        self._count = 0

    @property
    def current_item_index(self):
        return self._scenario.current_item_index

    @property
    def start_item_order(self):
        return self._start_item_order
    @start_item_order.setter
    def start_item_order(self, idx):
        self._start_item_order = idx

    @property
    def end_item_order(self):
        return int(self._scenario.get_item_order_number_by_index(
            self['repeat']['endItemNum']))

    @property
    def start_index(self):
        return int(self['repeat']['startIndex'])

    @property
    def end_index(self):
        return int(self['repeat']['endIndex'])

    @property
    def increment_index(self):
        return int(self['repeat']['incrementIndex'])

    @property
    def repeat_times(self):
        if self['repeat']['repeatType'] == 'Times':
            rt = str(self['repeat']['repeatTimesString'])
        else:
            rt = str(self['repeat']['repeatTimes'])
        code, data = self._variables.convert(rt)
        return int(data)

    @property
    def is_using_index(self):
        return self['repeat']['useIndex']

    # ==========================================================================
    @property
    def arguments(self):
        return

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        return make_follow_job_request(True, None, '')

    # ==========================================================================
    def get_next(self):
        """
        시나리오에서 다음 아이템 오더와 반복문의 조건을 비교
        current_item_index 에 지정
        :param args:
        :param kwargs:
        :return:
        """
        self.log_msg.push('Repeat')
        # 반복문 끝인지 검사 후 남아 있다면 시작 인덱스로 되돌림
        if self.current_item_index == self.end_item_order:
            self._count += 1
            self.logger.info(self.log_msg.format(
                "Reached at the end of this repeat."))
            self.logger.debug(StructureLogFormat(
                CUR_ITEM_INDEX=self.current_item_index,
                END_ITEM_INDEX=self.end_item_order,
                SET_REPEAT_TIMES=self._times,
                CUR_REPEAT_COUNT=self._count
            ))

            # 반복 횟 수가 남지 않은 상태
            if self._times == self._count:
                self.logger.info(self.log_msg.format(
                    'Reached at the end of the count.'))
                self._scenario._repeat_stack.pop()
                self.log_msg.pop()
                return self.current_item_index

            order_num = self.start_item_order
            if self.is_using_index:
                self.loop_index_increase(step=self.increment_index)
            self.logger.info(self.log_msg.format(
                'Back to the start of the repeat.'))
        else:
            order_num = self.current_item_index
            self.logger.info(self.log_msg.format('Set the next item.'))
        self.log_msg.pop()
        return order_num

    # ==========================================================================
    def loop_index_increase(self, path="{{rp.index}}", step=1):
        self.logger.info(self.log_msg.format(
            'Increased The Variable of the loop index.'))
        code, n = self._variables.get(path)
        self._variables.create("{{rp.index}}", int(n) + step)


################################################################################
class SendEmail(Items):
    # OCR
    references = ('imageMatch',)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        return


################################################################################
class ClearCache(Items):
    # OCR
    references = ('imageMatch',)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        return


################################################################################
class SetVariable(Items):
    # OCR
    references = ('setVariable',)
    # "setVariable": {
    #     "valueFromType": "Text",
    #     "textValue": "Labs",
    #     "GroupName": "ADDRESS",
    #     "VariableName": "TEXT_LABS",
    #     "IsArray": false},

    @property
    def arguments(self):
        variable_name = "{{%s.%s}}" % (
            self['setVariable']['GroupName'],
            self['setVariable']['VariableName'])
        return variable_name

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        self.log_msg.push('Set Variable')
        self.logger.info(self.log_msg.format('Calling...'))
        self._variables.create(self.arguments, self['setVariable']['textValue'])
        # TODO: 플러그인 아웃풋 처리
        self.log_msg.pop()
        return make_follow_job_request(True, None, '')



################################################################################
class Excel(Items):
    # OCR
    references = ('imageMatch',)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        return


################################################################################
class Navigate(Items):
    # OCR
    references = ('imageMatch',)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        return


################################################################################
class DocumentComplete(Items):
    # OCR
    references = ('imageMatch',)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        return


################################################################################
class Component(Items):
    # OCR
    references = ('imageMatch',)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        return


################################################################################
class TextMatch(Items):
    # OCR
    references = ('imageMatch',)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        return


################################################################################
class CompareText(Items):
    # OCR
    references = ('compareText', 'verifyResultAction')
    # "compareText": {"compareTextValues": [
    #     {"relationalOperator": null, "logicalOperator": "==",
    #      "leftValue": {"GroupName": "ABC", "VariableName": "ABC",
    #                    "VariableText": "{{ABC.ABC}}", "IsArray": false,
    #                    "varFormattedText": "{{ABC.ABC}}"},
    #      "rightValue": {"GroupName": "ABC", "VariableName": "DEF",
    #                     "VariableText": "1", "IsArray": false,
    #                     "varFormattedText": "{{ABC.DEF}}"}},
    #     {"relationalOperator": "And", "logicalOperator": "==",
    #      "leftValue": {"GroupName": "ABC", "VariableName": "ABC",
    #                    "VariableText": "1", "IsArray": false,
    #                    "varFormattedText": "{{ABC.ABC}}"},
    #      "rightValue": {"GroupName": "ABC", "VariableName": "ABC",
    #                     "VariableText": "1", "IsArray": false,
    #                     "varFormattedText": "{{ABC.ABC}}"}},
    #     {"relationalOperator": "Or", "logicalOperator": ">",
    #      "leftValue": {"GroupName": "ABC", "VariableName": "ABC",
    #                    "VariableText": "2", "IsArray": false,
    #                    "varFormattedText": "{{ABC.ABC}}"},
    #      "rightValue": {"GroupName": "ABC", "VariableName": "ABC",
    #                     "VariableText": "1", "IsArray": false,
    #                     "varFormattedText": "{{ABC.ABC}}"}},
    #     {"relationalOperator": "And", "logicalOperator": "<",
    #      "leftValue": {"GroupName": "ABC", "VariableName": "ABC",
    #                    "VariableText": "1", "IsArray": false,
    #                    "varFormattedText": "{{ABC.ABC}}"},
    #      "rightValue": {"GroupName": "ABC", "VariableName": "DEF",
    #                     "VariableText": "2", "IsArray": false,
    #                     "varFormattedText": "{{ABC.DEF}}"}}]

    # ==========================================================================
    @property
    @arguments_options_fileout
    def arguments(self):
        result = list()
        for value in self['compareText']['compareTextValues']:
            v = value.setdefault('relationalOperator', None)
            if v:
                result.append("-c")
                result.append(v.upper())
            _, v = self._variables.convert(value['leftValue']['VariableText'])
            result.append(v if v.isdigit() else json.dumps(v))
            # '>', '<' 리다이렉트 문자 보호
            v = value['logicalOperator']
            result.append(json.dumps(v) if len(v) == 1 else v)
            _, v = self._variables.convert(value['rightValue']['VariableText'])
            result.append(v if v.isdigit() else json.dumps(v))

        return tuple(result)

    # ==========================================================================
    @request_handler
    def __call__(self, *args, **kwargs):
        self.log_msg.push('Compare Text')
        cmd = 'python -m alabs.rpa.desktop.compare_text {}'.format(
            ' '.join(self.arguments))
        self.logger.info(self.log_msg.format('CompareText Calling...'))
        self.logger.debug(StructureLogFormat(CMD=cmd))

        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()

        if stderr:
            message = stderr.decode(self.locale)
            self.log_msg.pop()
            return self['verifyResultAction'], \
                   self['verifyResultAction']['failActionType'], \
                   message

        result = json.loads(stdout.decode(self.locale))
        message = ''
        action = {True: 'successActionType', False: 'failActionType'}[result]
        self.log_msg.pop()
        return self['verifyResultAction'], \
               self['verifyResultAction'][action], \
               message



################################################################################
class WaitingPopup(Items):
    # OCR
    references = ('imageMatch',)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        return


################################################################################
class DeleteFile(Items):
    # OCR
    references = ('imageMatch',)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        return


################################################################################
class ClosePopup(Items):
    # OCR
    references = ('imageMatch',)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        return

################################################################################
class EndScenario(Items):
    references = ()

    # ==========================================================================
    def __call__(self):
        self.log_msg.push('End Scenario')
        self.logger.info(self.log_msg.format('Calling...'))
        from alabs.pam.runner import ResultHandler
        function = (ResultHandler.SCENARIO_FINISH_SCENARIO.value, None)
        self.log_msg.pop()
        return make_follow_job_request(True, function, '')

################################################################################
class UserParams(Items):
    references = ('userInputs',)

    # ==========================================================================
    @property
    @arguments_options_fileout
    def arguments(self):
        data = self['userInputs']
        cmd = list()
        group_name = ""
        for d in data:
            group_name = d['groupName']
            cmd.append('--input')
            cmd.append(d['variableName'])
            cmd.append(json.dumps(d['defaultValue']))
            cmd.append(json.dumps(d['description']))
        cmd.insert(0, group_name)
        return tuple(cmd)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        # Continue to use 를 선택했을 경우 상태를 파일로 저장
        # 저장된 정보에서 Show에 Fasle가 있다면 저장된 값을 계속 사용
        self.log_msg.push('User Params')
        self.logger.info(self.log_msg.format('Calling...'))
        saved_var_file = os.environ.setdefault(
            'USER_PARAM_VARIABLES', 'user_param_variables.json')
        is_exists_saved_var_file = pathlib.Path(saved_var_file).exists()
        self.logger.debug(StructureLogFormat(
            SAVED_VAR_FILE_PATH=saved_var_file,
            IS_EXISTS=is_exists_saved_var_file))

        if is_exists_saved_var_file:
            data = json.loads(saved_var_file)
            status, function, message = self.get_result_handler(data)
            self.log_msg.pop()
            return make_follow_job_request(status, function, message)

        cmd = 'python -m alabs.rpa.autogui.user_parameters {}'.format(
            ' '.join(self.arguments))
        self.logger.debug(StructureLogFormat(CMD=cmd))

        with subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True) as proc:
            stdout = proc.stdout.read()
            stderr = proc.stderr.read()
            returncode = proc.returncode
        if stderr:
            self.logger.error(self.log_msg.format(stderr.decode()))
            self.log_msg.pop()
            return make_follow_job_request(False, message=stderr.decode())
        status, function, message = self.get_result_handler(
            data=json.loads(stdout.decode()))
        self.log_msg.pop()
        return make_follow_job_request(status, function, message)

    # ==========================================================================
    @staticmethod
    def get_result_handler(data=None):
        # data = {"show": True, "action": "ONCE", "group": "ABC",
        #         "values": [
        #             ["DEF", "D", "ABC"],
        #             ["GHI", "A", "DEDE"],
        #             ["XYZ", "Z", "AAA"]]}
        if not data:
            return False, None, "something wrong"
        status = True
        variable_form = '{{{{{}.{}}}}}'
        values = list()
        for v in data['values']:
            name = variable_form.format(data['group'], v[0])
            value = v[1]
            values.append((name, value))
        from alabs.pam.runner import ResultHandler
        function = (ResultHandler.VARIABLE_SET_VALUES.value, values)
        return status, function, ""


################################################################################
class PopupInteraction(Items):
    references = ('popupInteraction',)
    actions = {
        "Disuse": None,
        "Go": "MoveOn",
        "Resume scenario": "Resume",
        "FinishScenario": "AbortScenarioButNoError",
        "Error": "TreatAsError",
        "FinishStep": "IgnoreFailure",
        "Jump": "JumpForward",
        "BackJump": "JumpBackward",
        "Goto": "JumpToOperation",
        "StepJump": "JumpToStep",
        "Restart": "RestartFromTop"
    }

    # ==========================================================================
    @property
    @arguments_options_fileout
    def arguments(self):
        cmd = list()
        title = json.dumps(self['popupInteraction']['title'])
        if not title:
            title = json.dumps("No Message")
        cmd.append(title)
        cmd.append("--button")
        title = json.dumps(self['popupInteraction']['firstButtonTitle'])
        cmd.append(title)
        action = self.actions[
            self['popupInteraction']['firstButtonAction']]
        cmd.append(action)

        if self.actions[self['popupInteraction']['secondButtonAction']]:
            cmd.append("--button")
            title = json.dumps(self['popupInteraction']['secondButtonTitle'])
            cmd.append(title)
            action = self.actions[
                self['popupInteraction']['secondButtonAction']]
            cmd.append(action)

        if self.actions[self['popupInteraction']['thirdButtonAction']]:
            cmd.append("--button")
            title = json.dumps(self['popupInteraction']['thirdButtonTitle'])
            cmd.append(title)
            action = self.actions[self['popupInteraction']['thirdButtonAction']]
            cmd.append(action)
        return tuple(cmd)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        self.log_msg.push('Dialogue')
        self.logger.info(self.log_msg.format('Calling...'))
        from alabs.pam.runner import ResultHandler
        file = os.environ.setdefault('ACTION_STDOUT_FILE', 'action_stdout.log')
        if pathlib.Path(file).exists():
            pathlib.Path(file).unlink()

        cmd = 'python -m alabs.rpa.autogui.dialogue {}'.format(
            ' '.join(self.arguments))
        self.logger.debug(StructureLogFormat(CMD=cmd))

        with subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True) as proc:
            stdout = proc.stdout.read()
            stderr = proc.stderr.read()
            returncode = proc.returncode

        if stderr:
            self.logger.error(self.log_msg.format(stderr.decode()))
            return make_follow_job_request(
                False, message=stderr.decode(self.locale))

        # stdout = b'Button3,JumpForward'
        self.logger.info(self.log_msg.format('User clicked a button.'))
        act = stdout.decode().split(',')[1]
        self.logger.debug(StructureLogFormat(BUTTON=act))

        status = True
        function = None
        message = ''

        if act in ("MoveOn", "Resume"):
            pass
        elif act == "TreatAsError":
            status = False
            message = "User chose 'Treat as Error' button."
        elif act == "IgnoreFailure":
            function = (ResultHandler.SCENARIO_FINISH_STEP.value, None)
        elif act == "AbortScenarioButNoError":
            function = (ResultHandler.SCENARIO_FINISH_SCENARIO.value, None)
        else:
            pass
        self.log_msg.pop()
        return make_follow_job_request(status, function, message)


################################################################################
def excel_column_calculate(n:int, d:list):
    """
    Excel의 `A`, `AA` 와 같은 값을 Column 값을 쉽게 구할 수 있습니다.
    :param n: 첫 번째 Column 기준으로 1 이상의 수
    :param d: 빈 list
    :return: str
    >>> excel_column_calculate(1, []))
    'A'
    >>> excel_column_calculate(27, [])
    'AA'
    >>> excel_column_calculate(1000, [])
    'ALL'
    """
    if not n:
        return ''.join(d)
    n -= 1
    r = n // 26
    m = (n % 26)
    d.insert(0, chr(65 + m))
    return excel_column_calculate(r, d)


################################################################################
def result_as_csv(group, data:str, header=True):
    var_form = '{{{{{}.{}}}}}'
    # 줄 단위로 분리
    # [['name', 'address', 'data'],
    # ['Raven', 'deokyu@argos-labs.com', '1234'],
    # ['Benny', 'bkpark@argos-labs.com', '5678'],
    # ['Brad', 'brad@argos-labs.com', 'hello']]

    data = StringIO(data)
    data = csv.reader(data, delimiter=',')
    data = list(data)

    # 변수 이름 만들기
    # 헤더가 없다면 엑셀컬럼 순서로 생성
    if not data:
        return None
    if header:
        name = data.pop(0)
        name = [var_form.format(group, n) for n in name]
    else:
        name = [var_form.format(group, excel_column_calculate(i, []))
                for i, _ in enumerate(data[0], 1)]
    return tuple(zip(name, list(zip(*data))))


################################################################################
class Plugin(Items):

    references = ('pluginDumpspec', 'pluginResultType', 'pluginResultGroupName',
                  'pluginResultVariable', 'pluginResultFilePath',
                  'pluginResultHasHeader')
    # ==========================================================================
    @property
    def arguments(self):
        cmd = plugin_spec_parser(self['pluginDumpspec'])
        return cmd

    # ==========================================================================
    def return_value(self):
        self.logger.info('Plugin\'s return value')

        file = get_conf().get('/PATH/PLUGIN_STDOUT_FILE')

        with open(file, 'r', encoding='utf-8') as f:
            value = f.read()
            self.logger.debug(StructureLogFormat(PLUGIN_OUT=value))

        if self['pluginResultType'] == 'String':
            path = self['pluginResultVariable']['VariableText']
            self._variables.create(path, value)
        elif self['pluginResultType'] == 'CSV':
            group = self['pluginResultGroupName']
            header = self['pluginResultHasHeader']
            data = result_as_csv(group, value, header=header)
            if not data:
                return None
            for path, v in data:
                self._variables.create(path, v)
        elif self['pluginResultType'] == 'File':
            # File
            pathlib.Path(self['pluginResultFilePath']).write_text(value)
            path = self['pluginResultVariable']['VariableText']
            self._variables.create(path, self['pluginResultFilePath'])
        else:
            self.logger.warn('pluginResultType is None.')
            pass

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        self.log_msg.push('Plugin')
        self.logger.info(self.log_msg.format('Calling...'))
        # 플러그인 결과파일 삭제
        file = get_conf().get('/PATH/PLUGIN_STDOUT_FILE')
        if pathlib.Path(file).exists():
            pathlib.Path(file).unlink()
        env = os.environ.copy()
        cmd = ' '.join(['python', '-m'] + [self.arguments])
        self.logger.debug(StructureLogFormat(CMD=cmd))
        with subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, env=env) as proc:
            stdout = proc.stdout.read()
            stderr = proc.stderr.read()
            returncode = proc.returncode

        if stderr:
            # TODO: 플러그인 에러시 처리할 방법 필요
            try:
                self.logger.error(stderr.decode())
            except Exception as e:
                pass
            self.log_msg.pop()
            return make_follow_job_request(True, None, '')
            # return make_follow_job_request(False, message=stderr.decode())

        # TODO: 플러그인 아웃풋 처리
        self.return_value()
        self.log_msg.pop()
        return make_follow_job_request(True, None, '')










