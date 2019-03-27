import json
import codecs
import enum
import time
import subprocess
import pyautogui
import variable_parser
import pyperclip

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from contextlib import contextmanager



PROG_NAME = 'chrome.exe'
WEB_DRIVER = 'C:\\Program Files (x86)\\ARGOS\\AgentForRPA\\Win\\Library\\webdriver\\32bit\chromedriver.exe'

WAIT_BEFORE_START = lambda: time.sleep(0.2)

class TestOrder(enum.IntEnum):
    TEST_LOCATE_IMAGE = 0
    TEST_SCROLL = enum.auto()
    TEST_TYPE_INPUT = enum.auto()
    TEST_OCR = enum.auto()


################################################################################
def image_json(image_json):
    t = image_json['imageMatch']
    click_bt = t['clickType'] # Left
    click_motion_type = t['clickMotionType'] # DownAndUP
    crop_loction = t['cropImageLocation'] # 6, 23, 341, 38
    search_location = t['searchLocation'] # 0, 0, 1370, 175
    ocr_location =t['ocrLocation'] # 0, 0, 0, 0
    click_point = t['clickPoint'] # 0, 0
    crop_image_failname = t['cropImageFileName'] # temp_636809883314015123_2063bc454e9f437d871185dee5493053_1_CropImage.png
    # t['cropImageFileChecksum'] # 507365D4B05E2CF311818A1CBA282F23
    # t['ocrImageFileName'] #
    # t['ocrImageFileChecksum'] #
    similarity = t['similarity'] # '70'
    return click_bt

def image_match(image):
    WAIT_BEFORE_START()
    # todo: ImageMatch Action 생성 필요
    # todo: pyautogui의 locateCenterOnScreen 으로 대체
    result = pyautogui.locateOnScreen(image)
    if not result:
        print('-- The image is not matched')
        return None
    print('-- The image is matched')
    return result


################################################################################
def locate_image(image, rx, ry):
    result = image_match(image)
    if not result:
        return False
    x, y, *_ = result
    WAIT_BEFORE_START()
    pyautogui.click(x=x+rx, y=y+ry)
    return True

################################################################################
def scroll(v):
    v *= 120 / 3.5
    v *= -1
    pyautogui.vscroll(int(v))

def delay(v):
    time.sleep(v * 0.001)

def kill_process(prog_name):
    subprocess.Popen(['Taskkill', '/IM', prog_name, '/F'])


def set_variable_la(hdl, data):
    if data['valueFromType'] == "Text":
        hdl[data['GroupName']][data['VariableName']] = data['textValue']

def type_text(json_type_text, var_hdl=None):
    t = json_type_text['typeText']
    if t['typeTextType'] == 'UserVariable':
        if not var_hdl:
            raise Exception
        text = var_hdl[t['userVariableGroup']][t['userVariableName']]
    else:
        text = var_hdl.convert(t['keyValue'])
    pyautogui.typewrite(text)


with codecs.open("LA-Scenario0030.json", 'r', 'utf-8-sig') as f:
       scn = json.load(f)


@contextmanager
def wait_for_new_window(driver, title, timeout=10):
    driver.switch_to.window(driver.window_handles[-1])
    WAIT_BEFORE_START()
    yield
    WebDriverWait(driver, timeout).until(
        lambda driver: title == driver.title)



steps = scn['stepList']
step_0 = steps[0]
# print(json.dumps(step_0))


# step_1 = steps[1]
# step_2 = steps[2]
# step_3 = steps[3]
# step_4 = steps[4]


################################################################################
# 변수 선언
variable_list = scn['userVariableList']
variables = variable_parser.VariableForLa()
for var in variable_list:
    variables.create(var['GroupName'], var['VariableName'])

################################################################################
# 스텝 1
# Open Web Browser
# 브라우져를 실행하는 스탭

# SetVariables
# OpenBrowser
# Delay
# ImageMatch
# LocateImage
# ImageMatch


items = steps[0]['items']

# SetVariables
WAIT_BEFORE_START()
set_variable_la(variables, items[0]['setVariable'])

# OpenBrowser
WAIT_BEFORE_START()
webhdl = webdriver.Chrome(WEB_DRIVER)
webhdl.get(variables.convert(items[1]['navigate']['URL']))

# Delay
# todo: 시간 변경
WAIT_BEFORE_START()
value = step_0['items'][2]['delay']['delay']
delay(int(value))

# ImageMatch
WAIT_BEFORE_START()
# todo: ImageMatch Action 생성 필요
# todo: pyautogui의 locateCenterOnScreen 으로 대체
image = 'Images\TestRunScenario.json\\' + items[3]['imageMatch']['cropImageFileName']
result = image_match(image)
if not result:
    subprocess.Popen(['Taskkill /IM chrome.exe /F'])
    exit(0)

# LocateImage
# todo: LocateImage 사용
WAIT_BEFORE_START()
import json
# print(json.dumps(items[6]))
image = 'Images\TestRunScenario.json\\' + items[4]['imageMatch']['cropImageFileName']
image_match(image)
click_pos = items[4]['imageMatch']['clickPoint']
x, y = [int(v) for v in click_pos.split(',')]  # '23, 45' 문자열을 변환
result = locate_image(image, x, y)
if not result:
    raise Exception

# ImageMatch
WAIT_BEFORE_START()
# todo: ImageMatch Action 생성 필요
# todo: pyautogui의 locateCenterOnScreen 으로 대체
image = 'Images\TestRunScenario.json\\' + items[5]['imageMatch']['cropImageFileName']
result = image_match(image)
if not result:
    subprocess.Popen(['Taskkill /IM chrome.exe /F'])
    raise Exception





################################################################################
# 스텝 2
items = steps[1]['items']

# HTMLAction - Check
# ShortcutKeys
# OnloadEvent
# ImageMatch

# HTMLAction
WAIT_BEFORE_START()
el = webhdl.find_element_by_xpath('//body/*/input[@name="vehicle2"]')
el.click()


# Send HotKey
WAIT_BEFORE_START()
pyautogui.hotkey('tab')
WAIT_BEFORE_START()
pyautogui.hotkey('enter')

# OnloadEvent
WAIT_BEFORE_START()
webhdl.implicitly_wait(5)

# ImageMatch
WAIT_BEFORE_START()
image = 'Images\TestRunScenario.json\\' + items[3]['imageMatch']['cropImageFileName']
image_match(image)

# click_pos = items[6]['imageMatch']['clickPoint']
# x, y = [int(v) for v in click_pos.split(',')]  # '23, 45' 문자열을 변환
# result = locate_image(image, x, y)
# if not result:
#     kill_process(PROG_NAME)


################################################################################
# 스텝 3
# JavaScript

# setVariables
# JavaScript

items = steps[2]['items']

# setVariables
WAIT_BEFORE_START()
set_variable_la(variables, items[0]['setVariable'])

# JavaScript
WAIT_BEFORE_START()
script = items[1]['browserScript']['script']
webhdl.execute_script(script)


################################################################################
# 스텝 4
# WaitingPopup
# ImageMatch
# ClosePopup
# ImageMatch
# Javascript

# delay(5000)
# webhdl.implicitly_wait(10)
time.sleep(5)

items = steps[3]['items']

# WaitingPopup
title = items[0]['watingPopup']['title']
title = title.split('-')[0].strip()
with wait_for_new_window(webhdl, title):
    pass

# ImageMatch
WAIT_BEFORE_START()
image = 'Images\TestRunScenario.json\\' + items[1]['imageMatch']['cropImageFileName']
image_match(image)

# ClosePopup
pyautogui.hotkey('ctrlleft', 'w')
webhdl.switch_to.window(webhdl.window_handles[-1])

# ImageMatch
WAIT_BEFORE_START()
image = 'Images\TestRunScenario.json\\' + items[3]['imageMatch']['cropImageFileName']
image_match(image)

# JavaScript
WAIT_BEFORE_START()
script = items[4]['browserScript']['script']
webhdl.execute_script(script)


################################################################################
# 스탭 5

items = steps[4]['items']

# Delay
# todo: 시간 변경
WAIT_BEFORE_START()
value = items[0]['delay']['delay']
delay(int(value))

webhdl.close()