#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod:`alabs.pam
====================================
.. moduleauthor:: Duk Kyu Lim (deokyu@argos-labs.com)
.. note:: VIVANS License

Description
===========
ARGOS LABS PAM For LA

Authors
===========

* Duk Kyu Lim

Change Log
--------

"""

################################################################################
import os
import platform
import argparse
from selenium import webdriver



################################################################################
# Version
NUM_VERSION = (0, 9, 0)
VERSION = ".".join(str(nv) for nv in NUM_VERSION)
__version__ = VERSION

OWNER = 'ARGOS-LABS'
GROUP = 'Pam'
PLATFORM = ['windows', 'darwin']
OUTPUT_TYPE = 'json'
DESCRIPTION = 'Pam for HA. It reads json scenario files by LA Stu and runs'


################################################################################
def create_driver_session(session_id, executor_url):
    from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
    # 명령어 Non-Blocking 설정
    from selenium.webdriver.common.desired_capabilities import \
        DesiredCapabilities
    caps = DesiredCapabilities().CHROME
    # caps["pageLoadStrategy"] = "normal"  # complete
    # caps["pageLoadStrategy"] = "eager"  #  interactive
    caps["pageLoadStrategy"] = "none"



    # Save the original function, so we can revert our patch
    org_command_execute = RemoteWebDriver.execute

    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return org_command_execute(self, command, params)

    # Patch the function before creating the driver object
    RemoteWebDriver.execute = new_command_execute

    new_driver = webdriver.Remote(command_executor=executor_url,
                                  desired_capabilities=caps)
    new_driver.session_id = session_id

    # Replace the patched function with original function
    RemoteWebDriver.execute = org_command_execute

    return new_driver


################################################################################
def check(driver, el, value):
    if value not in ('true', 'false'):
        raise ValueError(
            f'The check option is only allow true or false. not {value}.')
    driver.execute_script("arguments[0].check(arguments[1])", el, value)


################################################################################
def set_value(driver, el, value):
    driver.execute_script("arguments[0].value = arguments[1]", el, value)


################################################################################
def submit(driver, el, value=None):
    driver.execute_script("arguments[0].submit()", el)


################################################################################
def select(driver, el, value):
    js = """function setSelectedValue(selectObj, valueToSet) {
    for (var i = 0; i < selectObj.options.length; i++) {
        if (selectObj.options[i].text== valueToSet) {
            selectObj.options[i].selected = true;
            return;
        }
    }}
    setSelectedValue(arguments[0], arguments[1]);
    """
    driver.execute_script(js, el, value)


################################################################################
def click(driver, el, value=None):
    driver.execute_script("arguments[0].click()", el)


################################################################################
def tags_to_xpath_parser(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('tag_name', type=str, help='tag name')
    parser.add_argument('attr_type', choices=[
        'class', 'id', 'name', 'src', 'href'], help='Attribute type')
    parser.add_argument('attr_value', type=str)
    return parser.parse_args(args).__dict__


################################################################################
def tags_to_xpath(args):
    value = tags_to_xpath_parser(args)
    # xpath = f'//body/*/{tag_name}\[@{attr_type}="{attr_value}"]'.format(value)
    xpath = '//{tag_name}[@{attr_type}="{attr_value}"]'.format(**value)
    return xpath


################################################################################
def main(*args):
    _platform = os.environ.get('ARGOS_RPA_PAM_PLATFORM', platform.system())
    if _platform == 'Linux':
        from alabs.pam.rpa.web.html_action.linux import main as _main
    elif _platform == 'Windows':
        from alabs.pam.rpa.web.html_action.linux import main as _main
    elif _platform == 'Darwin':
        from alabs.pam.rpa.web.html_action.linux import main as _main

    else:
        raise Exception("{} is Not Supported Platform".format(_platform))
    return _main(*args)
