import json
import codecs
import enum
import time
import subprocess
import pyautogui


PROG_NAME = 'chrome.exe'
WAIT_BEFORE_START = lambda: time.sleep(0.2)

class TestOrder(enum.IntEnum):
    TEST_LOCATE_IMAGE = 0
    TEST_SCROLL = enum.auto()
    TEST_TYPE_INPUT = enum.auto()
    TEST_OCR = enum.auto()


################################################################################
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



with codecs.open("TestRunScenario.json", 'r', 'utf-8-sig') as f:
       scn = json.load(f)

steps = scn['stepList']
step_0 = steps[0]
step_1 = steps[1]
step_2 = steps[2]
step_3 = steps[3]
step_4 = steps[4]


################################################################################
# 스텝 1
# RunProgram
# Delay
# ImageMatch

# RunProgram
WAIT_BEFORE_START()
value = step_0['items'][0]['executeProcess']['executeFilePath']
value = value.split()
value[0] = "c:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
subprocess.Popen([*value])
print('-- Executed Chrome Browser as full screen')

# Delay
# todo: 시간 변경
WAIT_BEFORE_START()
value = step_0['items'][1]['delay']['delay']
delay(int(value))
print('-- delay 4 seconds')

# ImageMatch
WAIT_BEFORE_START()
# todo: ImageMatch Action 생성 필요
# todo: pyautogui의 locateCenterOnScreen 으로 대체
image = 'Images\TestRunScenario.json\\' + step_0['items'][2]['imageMatch']['cropImageFileName']
result = image_match(image)
if not result:
    subprocess.Popen(['Taskkill /IM chrome.exe /F'])


################################################################################
# 스텝 2
# LocateImage
# todo: LocateImage 사용
WAIT_BEFORE_START()
image = 'Images\TestRunScenario.json\\' + step_1['items'][0]['imageMatch']['cropImageFileName']
click_pos = step_1['items'][0]['imageMatch']['clickPoint']
x, y = [int(v) for v in click_pos.split(',')]  # '23, 45' 문자열을 변환
result = locate_image(image, x, y)
if not result:
    kill_process(PROG_NAME)


# ImageMatch
# todo: pyautogui의 locateCenterOnScreen 으로 대체
WAIT_BEFORE_START()
image = 'Images\TestRunScenario.json\\' + step_1['items'][1]['imageMatch']['cropImageFileName']
image_match(image)

################################################################################
# 스텝 3
# Scroll
# Scroll 사용
# Click and Focus
# ImageMatch

# Scroll
WAIT_BEFORE_START()
v = int(step_2['items'][0]['mouseScroll']['scrollLines'])  # '40'
scroll(v)

# Click and Foucs
WAIT_BEFORE_START()
pos = step_2['items'][1]['mouseClick']['clickPoint']  # '147, 649
x, y = [int(v) for v in pos.split(',')]
pyautogui.click(x, y)

# ImageMatch
WAIT_BEFORE_START()
image = 'Images\TestRunScenario.json\\' + step_2['items'][2]['imageMatch']['cropImageFileName']
image_match(image)

################################################################################
# 스텝 4
# LocateImage
# TextInput
# ShortcutKeys
# ImageMatch

# LocateImage
WAIT_BEFORE_START()
image = 'Images\TestRunScenario.json\\' + step_3['items'][0]['imageMatch']['cropImageFileName']
click_pos = step_3['items'][0]['imageMatch']['clickPoint']
x, y = [int(v) for v in click_pos.split(',')]  # '23, 45' 문자열을 변환
result = locate_image(image, x, y)

# TextInput
WAIT_BEFORE_START()
text = step_3['items'][1]['typeText']['keyValue']
pyautogui.typewrite(text)

# Send HotKey
WAIT_BEFORE_START()
pyautogui.hotkey('enter')

# ImageMatch
image = 'Images\TestRunScenario.json\\' + step_3['items'][3]['imageMatch']['cropImageFileName']
image_match(image)

################################################################################
# 스텝 5
# OCR
# LocateImage
# TextInput
# ShortcutKey
# ImageMatch
# Delay
# time.sleep 사용
# KillProcess

# OCR
# todo: OCR은 차후 진행

# LocateImage
WAIT_BEFORE_START()
image = 'Images\TestRunScenario.json\\' + step_4['items'][1]['imageMatch']['cropImageFileName']
click_pos = step_4['items'][1]['imageMatch']['clickPoint']
x, y = [int(v) for v in click_pos.split(',')]
result = locate_image(image, x, y)

# TypeInput
# todo: OCR 결과 값으로 수정 필요

# TypeInput
# todo: OCR 결과 값으로 수정 필요
WAIT_BEFORE_START()
pyautogui.typewrite('ArgosLabs')

# SendHotKey
WAIT_BEFORE_START()
pyautogui.hotkey('enter')

# ImageMatch
WAIT_BEFORE_START()
image = 'Images\TestRunScenario.json\\' + step_4['items'][5]['imageMatch']['cropImageFileName']
image_match(image)

# Delay
WAIT_BEFORE_START()
value = step_4['items'][6]['delay']['delay']
time.sleep(int(value))

# KillProcess
WAIT_BEFORE_START()
kill_process(PROG_NAME)


