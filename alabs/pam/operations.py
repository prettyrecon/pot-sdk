import pathlib
import enum
import subprocess
import os
import json
from functools import wraps
from alabs.rpa.desktop.execute_process import main as execute_process
from alabs.rpa.desktop.delay import main as delay
from alabs.rpa.autogui.locate_image import main as locate_image
from alabs.rpa.autogui.scroll import main as scroll
from alabs.rpa.autogui.click import main as click
from alabs.rpa.autogui.type_text import main as type_text
from alabs.rpa.autogui.send_shortcut import main as send_short_cut
from alabs.rpa.autogui.find_image_location import main as image_match
from alabs.pam.dumpspec_parser import plugin_spec_parser
from alabs.pam.variable_manager.rc_api_variable_manager import \
    VariableManagerAPI

from alabs.pam.runner import ResultHandler


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
        stdout = os.environ.setdefault(
            'OPERATION_STDOUT_FILE', 'operation.stdout')
        if stdout:
            arguments += ['--outfile ', stdout]
        pam_log = os.environ.setdefault('PAM_LOG', 'pam.log')
        if pam_log:
            arguments += ['--errfile ', pam_log]
            arguments += ['--logfile', pam_log]
        return tuple(arguments)
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
        self._scenario = scenario
        for r in self.item_ref:
            self[r] = data[r]
        for r in self.references:
            self[r] = data[r]

        self._variables = VariableManagerAPI(pid=str(os.getpid()),
                                             logger=logger)

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
    @arguments_options_fileout
    def arguments(self)-> tuple:
        return self['executeProcess']['executeFilePath']

    # ==========================================================================
    def __call__(self):
        execute_process(self.arguments)
        return


################################################################################
class Delay(Items):
    item_type = Items.Type.EXECUTABLE_ITEM
    references = ('delay',)
    # {'delay': {'delay': '4000'}}

    # ==========================================================================
    @property
    def arguments(self)->tuple:
        return self['delay']['delay'],

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        return delay(self.arguments[0])


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
    def arguments(self) -> tuple:
        cmd = list()
        # filename
        import pathlib
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

        if m == ClickType['DOUBLE'].name:
            b = ClickType['DOUBLE'].name
            m = ClickType['LEFT'].name

        cmd.append('--button')
        cmd.append(b)

        cmd.append('--motion')
        cmd.append(m)
        return tuple(cmd)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        cmd = 'python -m alabs.rpa.autogui.locate_image {}'.format(
            ' '.join(self.arguments))
        subprocess.Popen(cmd, shell=True)
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
    def __call__(self, *args, **kwargs):
        return image_match(*self.arguments)


################################################################################
class MouseScroll(Items):
    item_type = Items.Type.EXECUTABLE_ITEM
    references = ('mouseScroll',)
    # 'mouseScroll': {'scrollX': '0', 'scrollY': '0', 'scrollLines': '40'}
    # ==========================================================================
    @property
    def arguments(self) -> tuple:
        v = int(self['mouseScroll']['scrollLines'])
        return '--vertical', v

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        v = int(self['mouseScroll']['scrollLines'])
        cmd = 'python -m alabs.rpa.autogui.scroll {}'.format(
            ' '.join([str(x) for x in self.arguments]))
        subprocess.Popen(cmd, shell=True)
        # return scroll(*self.arguments)


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

        if m == ClickType['DOUBLE'].name:
            b = ClickType['DOUBLE'].name
            m = ClickType['LEFT'].name

        cmd.append('--button')
        cmd.append(b)

        cmd.append('--motion')
        cmd.append(m)
        return tuple(cmd)

    # ==========================================================================
    def __call__(self, *args, **kwargs):

        cmd = 'python -m alabs.rpa.autogui.click {}'.format(
            ' '.join(self.arguments))
        subprocess.Popen(cmd, shell=True)
        # return click(*self.arguments)

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
    def arguments(self) -> tuple:
        _type = self['typeText']['typeTextType']
        if "Text" == _type:
            value = self['typeText']['keyValue']
        elif "UserVariable" == _type:
            variable_name = "{{%s.%s}}" % (
                self['typeText']['userVariableGroup'],
                self['typeText']['userVariableName'])
            code, value = self._variables.get(variable_name)
        else:
            # Saved Data
            value = ""
            # raise ValueError("Not Supported Yet")
        # 리눅스 Bash에서 해당 문자열은 멀티라인을 뜻하므로 이스케이프문자 처리
        value = value.replace('`', '\`')
        return value,

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        cmd = 'python -m alabs.rpa.autogui.type_text {}'.format(
            json.dumps(' '.join(self.arguments)))
        subprocess.Popen(cmd, shell=True)
        # return type_text(*self.arguments)


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
            value.append(('--txt', k['txt']))

        return tuple(value)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        for arg in self.arguments:
            cmd = 'python -m alabs.rpa.autogui.send_shortcut {}'.format(
                ' '.join(arg))
            subprocess.Popen(cmd, shell=True)
            # send_short_cut(*arg)
        return True


################################################################################
class StopProcess(Items):
    references = ('stopProcess',)
    # 'mouseScroll': {'scrollX': '0', 'scrollY': '0', 'scrollLines': '40'}

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        return

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
class Repeat(Items):
    references = ('repeat',)

    # ==========================================================================
    def __init__(self, data:dict, scenario, logger):
        Items.__init__(self, data, scenario, logger)
        self._scenario._current_item_index  = self.start_index - 1
        self._times = self.repeat_times

    @property
    def start_index(self):
        return self['repeat']['startIndex']

    @property
    def end_index(self):
        return self['repeat']['endIndex']

    @property
    def increment_index(self):
        return self['repeat']['incrementIndex']

    @property
    def repeat_times(self):
        return self['repeat']['repeatTimes']

    # ==========================================================================
    @property
    def arguments(self):
        return

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        item = self._scenario.item
        if self._times == 1:
            self._scenario.set_current_item_by_index(self.end_index)
            item = self._scenario.item
            self._scenario._repeat_item = None
            return item

        if self.end_index == item['index']:
            self._times -= 1
            self._scenario.set_current_item_by_index(self.start_index)
            item = self._scenario.item
            return item

        return item


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
        self._variables.create(self.arguments, self['textValue'])
        return


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
    def __call__(self, *args, **kwargs):
        return

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
            cmd.append('--question')
            cmd.append(d['variableName'])
            cmd.append(json.dumps(d['defaultValue']))
        cmd.insert(0, group_name)
        return tuple(cmd)

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        cmd = 'python -m alabs.rpa.autogui.user_parameters {}'.format(
            ' '.join(self.arguments))

        with subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True) as proc:
            stdout = proc.stdout.read()
            stderr = proc.stderr.read()
            returncode = proc.returncode

        print(stdout, stderr, returncode)


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

        file = os.environ.setdefault('ACTION_STDOUT_FILE', 'action_stdout.log')
        if pathlib.Path(file).exists():
            pathlib.Path(file).unlink()

        cmd = 'python -m alabs.rpa.autogui.dialogue {}'.format(
            ' '.join(self.arguments))

        with subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True) as proc:
            stdout = proc.stdout.read()
            stderr = proc.stderr.read()
            returncode = proc.returncode

        if stderr:
            return make_follow_job_request(False, message=stderr.decode())

        # stdout = b'Button3,JumpForward'
        act = stdout.decode().split(',')[1]

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
        return make_follow_job_request(status, function, message)




################################################################################
class Plugin(Items):

    references = ('pluginDumpspec', 'pluginResultType', 'pluginResultGroupName',
                  'pluginResultVariable', 'pluginResultFilePath')
    # ==========================================================================
    @property
    def arguments(self):
        cmd = plugin_spec_parser(self['pluginDumpspec'])
        return cmd

    def return_value(self):

        file = os.environ.setdefault('PLUGIN_STDOUT_FILE', 'plugin_stdout.log')
        with open(file, 'r') as f:
            value = f.read()

        if self['pluginResultType'] == 'String':
            path = self['pluginResultVariable']['VariableText']
            self._variables.create(path, value)
        elif self['pluginResultType'] == 'CSV':
            pass
        else:
            # File
            pathlib.Path(self['pluginResultFilePath']).write_text(value)
            path = self['pluginResultVariable']['VariableText']
            self._variables.create(path, self['pluginResultFilePath'])
        pass

    # ==========================================================================
    def __call__(self, *args, **kwargs):
        # 플러그인 결과파일 삭제
        file = os.environ.setdefault('PLUGIN_STDOUT_FILE', 'plugin_stdout.log')
        if pathlib.Path(file).exists():
            pathlib.Path(file).unlink()

        cmd = ' '.join(['python', '-m'] + [self.arguments])
        with subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True) as proc:
            stdout = proc.stdout.read()
            stderr = proc.stderr.read()
            returncode = proc.returncode

        # TODO: 플러그인 아웃풋 처리
        self.return_value()

        return









