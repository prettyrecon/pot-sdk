"""
====================================
 :mod:`alabs.selenium`
====================================
.. moduleauthor:: Jerry Chae <mcchae@argos-labs.com>
.. note:: ARGOS-LABS License

Description
===========
ARGOS LABS base class to use Selenium
"""
# Authors
# ===========
#
# * Jerry Chae
#
# Change Log
# --------
#
#  * [2021/01/17]
#     - get_by_xpath에 move_to_element flag 추가
#  * [2020/12/02]
#     - starting

import os
import sys
import csv
import xlrd
import time
import glob
import shutil
import locale
import logging
import requests
import traceback
import subprocess
from tempfile import gettempdir
from zipfile import ZipFile
# for selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select


################################################################################
class PySelenium(object):
    # ==========================================================================
    BROWSERS = {
        'Chrome': {
            'driver-download-link': [
                {
                    'version': '88',
                    'link': {
                        'win32': 'https://chromedriver.storage.googleapis.com/88.0.4324.96/chromedriver_win32.zip',
                        'linux': 'https://chromedriver.storage.googleapis.com/88.0.4324.96/chromedriver_linux64.zip',
                        'darwin': 'https://chromedriver.storage.googleapis.com/88.0.4324.96/chromedriver_mac64.zip',
                        # todo: 'darwin_m1': 'https://chromedriver.storage.googleapis.com/88.0.4324.96/chromedriver_mac64_m1.zip',
                    }
                },
                {
                    'version': '87',
                    'link': {
                        'win32': 'https://chromedriver.storage.googleapis.com/87.0.4280.20/chromedriver_win32.zip',
                        'linux': 'https://chromedriver.storage.googleapis.com/87.0.4280.20/chromedriver_linux64.zip',
                        'darwin': 'https://chromedriver.storage.googleapis.com/87.0.4280.20/chromedriver_mac64.zip',
                    }
                },
                {
                    'version': '86',
                    'link': {
                        'win32': 'https://chromedriver.storage.googleapis.com/86.0.4240.22/chromedriver_win32.zip',
                        'linux': 'https://chromedriver.storage.googleapis.com/86.0.4240.22/chromedriver_linux64.zip',
                        'darwin': 'https://chromedriver.storage.googleapis.com/86.0.4240.22/chromedriver_mac64.zip',
                    },
                },
                {
                    'version': '85',
                    'link': {
                        'win32': 'https://chromedriver.storage.googleapis.com/85.0.4183.87/chromedriver_win32.zip',
                        'linux': 'https://chromedriver.storage.googleapis.com/85.0.4183.87/chromedriver_linux64.zip',
                        'darwin': 'https://chromedriver.storage.googleapis.com/85.0.4183.87/chromedriver_mac64.zip',
                    },
                },
            ]
        },
        'Edge': {
            'driver-download-link': [
                {
                    'version': '*',
                    'link': {
                        'win32': 'https://msedgedriver.azureedge.net/{version}/edgedriver_win32.zip',
                        'darwin': 'https://msedgedriver.azureedge.net/{version}/edgedriver_mac64.zip',
                    }
                },
            ]
        }
        # 'Firefox',
    }
    CACHE_FOLDER = os.path.join(gettempdir(), 'PySelenium.cahce')
    EXP_COND = {
        'title_is': EC.title_is,
        'title_contains': EC.title_contains,
        'presence_of_element_located': EC.presence_of_all_elements_located,
        'visibility_of_element_located': EC.visibility_of_element_located,
        'visibility_of': EC.visibility_of,
        'presence_of_all_elements_located': EC.presence_of_all_elements_located,
        'text_to_be_present_in_element': EC.text_to_be_present_in_element,
        'text_to_be_present_in_element_value': EC.text_to_be_present_in_element_value,
        'frame_to_be_available_and_switch_to_it': EC.frame_to_be_available_and_switch_to_it,
        'invisibility_of_element_located': EC.invisibility_of_element_located,
        'element_to_be_clickable': EC.element_to_be_clickable,
        'staleness_of': EC.staleness_of,
        'element_to_be_selected': EC.element_to_be_selected,
        'element_located_to_be_selected': EC.element_located_to_be_selected,
        'element_selection_state_to_be': EC.element_selection_state_to_be,
        'element_located_selection_state_to_be': EC.element_located_selection_state_to_be,
        'alert_is_present': EC.alert_is_present,
    }

    # ==========================================================================
    def _get_browser_version(self):
        if self.platform == 'win32':
            if self.browser == 'Chrome':
                cmd = [
                    'powershell',
                    '-command',
                    r"(Get-Item (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe').'(Default)').VersionInfo",
                ]
                # '''
                # ProductVersion   FileVersion      FileName
                # --------------   -----------      --------
                # 87.0.4280.66     87.0.4280.66     C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
                # '''
                po = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                po.wait()
                out = po.stdout.read().decode().strip()
                if out.find('ProductVersion') <= 0:
                    lines = out.split('\n')
                    bv = lines[-1].split()[0]
                    return bv.split('.')[0]
                else:
                    raise IOError(f'"{self.browser}" is not installed is this system')
            # todo: "Edge Legacy"
            elif self.browser == 'Edge':
                cmd = [
                    'reg.exe',
                    'QUERY',
                    "HKEY_CURRENT_USER\Software\Microsoft\Edge\BLBeacon",
                    '/t',
                    'REG_SZ',
                    '/reg:32',
                    '/v',
                    'version',
                ]
                # '''
                # HKEY_CURRENT_USER\Software\Microsoft\Edge\BLBeacon
                #     version    REG_SZ    88.0.705.50
                # '''
                po = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                po.wait()
                os_encoding = locale.getpreferredencoding()
                out = po.stdout.read().decode(os_encoding).strip()
                for line in out.split('\n'):
                    line = line.strip()
                    if line.startswith('version'):
                        return line.split()[-1]
                raise IOError(f'"{self.browser}" is not installed is this system')
            else:
                raise NotImplementedError(f'to get {self.browser} browser version')
        else:
            raise NotImplementedError('Linux, Mac need to be get browser version')

    # ==========================================================================
    def _get_web_driver(self, drive_f):
        if self.browser == 'Chrome':
            return webdriver.Chrome(executable_path=drive_f)
        if self.browser == 'Edge':
            return webdriver.Edge(executable_path=drive_f)
        raise NotImplementedError(f'Need to implement for the driver {self.browser} at {self.platform}')

    # ==========================================================================
    def _get_download_url(self):
        for dwl in self.BROWSERS[self.browser].get('driver-download-link', []):
            if self.browser == 'Chrome':
                if self.browser_version.startswith(dwl['version']):
                    if self.platform not in dwl['link']:
                        raise ReferenceError(f'Cannot get driver link for the platform "{self.platform}"')
                    return dwl['link'][self.platform]
            elif self.browser == 'Edge':
                if dwl['version'] == '*':
                    return dwl['link'][self.platform].format(version=self.browser_version)
        raise ReferenceError(f'Cannot get driver link for the version "{self.browser_version}"')

    # ==========================================================================
    def _download_driver(self, drive_f):
        # download and save to cache
        url = self._get_download_url()
        r = requests.get(url, allow_redirects=True)
        is_unzip = url.lower().endswith('.zip')
        if is_unzip:
            with open(f'{drive_f}.zip', 'wb') as ofp:
                ofp.write(r.content)
            tmp_d = os.path.join(gettempdir(), os.path.basename(drive_f))
            with ZipFile(f'{drive_f}.zip') as zfp:
                zflist = zfp.namelist()
            wd_name = None
            for zf in zflist:
                if zf.find('/') > 0 or zf.find('\\') > 0:
                    continue
                wd_name = zf
                break
            if not wd_name:
                raise ReferenceError(f'Cannot find webdriver at "{drive_f}.zip"')
            with ZipFile(f'{drive_f}.zip') as zfp:
                zfp.extract(wd_name, tmp_d)
            for f in glob.glob(os.path.join(tmp_d, '*')):
                shutil.move(f, drive_f)
                break
            shutil.rmtree(tmp_d)
            os.remove(f'{drive_f}.zip')
        else:
            with open(drive_f, 'wb') as ofp:
                ofp.write(r.content)

    # ==========================================================================
    def _get_driver(self):
        if not os.path.exists(self.CACHE_FOLDER):
            os.makedirs(self.CACHE_FOLDER)
        bn = f'{self.platform}_{self.browser}_{self.browser_version}.exe'
        drive_f = os.path.join(self.CACHE_FOLDER, bn)
        if os.path.exists(drive_f):
            return self._get_web_driver(drive_f)
        self._download_driver(drive_f)
        if os.path.exists(drive_f):
            return self._get_web_driver(drive_f)
        raise RuntimeError(f'Cannot get web driver')

    # ==========================================================================
    def __init__(self, browser='Chrome', url='www.google.com',
                 width=1200, height=800, logger=None):
        try:
            if browser not in self.BROWSERS:
                raise ReferenceError(f'Cannot get info for the browser "{browser}"')
            self.browser = browser
            self.url = url
            self.width = width
            self.height = height
            if logger is None:
                logger = logging.getLogger('PySelenium')
            self.logger = logger
            # for internal uses
            self.platform = sys.platform
            self.browser_version = self._get_browser_version()
            self.driver = None
            self.main_handle = None
        except Exception as err:
            _exc_info = sys.exc_info()
            _out = traceback.format_exception(*_exc_info)
            del _exc_info
            self.logger.error('open Error: %s\n' % str(err))
            self.logger.error('%s\n' % ''.join(_out))
            raise

    # ==========================================================================
    def open(self):
        try:
            self.driver = self._get_driver()
            self.driver.set_window_size(self.width, self.height)
            self.driver.get(self.url)
            self.logger.info(f'open: get <{self.url}> with <{self.width},{self.height}>')
            self.implicitly_wait()
        except Exception as e:
            _exc_info = sys.exc_info()
            _out = traceback.format_exception(*_exc_info)
            del _exc_info
            self.logger.error('open Error: %s\n' % str(e))
            self.logger.error('%s\n' % ''.join(_out))
            raise

    # ==========================================================================
    def close(self):
        try:
            self.driver.close()
            self.logger.info(f'closed')
        except Exception as e:
            _exc_info = sys.exc_info()
            _out = traceback.format_exception(*_exc_info)
            del _exc_info
            self.logger.error('close Error: %s\n' % str(e))
            self.logger.error('%s\n' % ''.join(_out))
            raise

    # ==========================================================================
    def __enter__(self):
        self.open()
        return self

    # ==========================================================================
    def __exit__(self, *args):
        self.close()

    # ==========================================================================
    def implicitly_wait(self, imp_wait=3, after_wait=1):
        try:
            if imp_wait > 0:
                self.driver.implicitly_wait(imp_wait)
            if after_wait > 0:
                time.sleep(after_wait)
        except Exception as e:
            _exc_info = sys.exc_info()
            _out = traceback.format_exception(*_exc_info)
            del _exc_info
            self.logger.error('implicitly_wait Error: %s\n' % str(e))
            self.logger.error('%s\n' % ''.join(_out))
            raise

    # ==========================================================================
    def get_by_xpath(self, xp, timeout=10,
                     cond='presence_of_element_located',
                     cond_text=None,
                     wait_until_valid_text=False,
                     move_to_element=False):
        if cond not in self.EXP_COND:
            cond = None
        if not cond:
            return self.driver.find_element_by_xpath(xp)
        cond_f = self.EXP_COND[cond]
        args = [(By.XPATH, xp)]
        if cond in ('text_to_be_present_in_element', 'text_to_be_present_in_element_value'):
            args.append(cond_text)
        e = WebDriverWait(self.driver, timeout).until(cond_f(*args))
        if isinstance(e, bool):
            cond_f = self.EXP_COND['presence_of_element_located']
            args = [(By.XPATH, xp)]
            e = WebDriverWait(self.driver, timeout).until(cond_f(*args))
        if isinstance(e, list):
            e = e[0]
        if not isinstance(e, WebElement):
            print(e)
        if wait_until_valid_text:
            for i in range(timeout):
                if e.text:
                    break
                time.sleep(1)
                self.logger.debug(f'get_by_xpath: waiting valid text ... [{i+1}]')
        if move_to_element:
            # actions = ActionChains(self.driver)
            # actions.move_to_element(e).perform()
            self.driver.execute_script('arguments[0].scrollIntoView();', e)
        return e

    # ==========================================================================
    def key_action(self, key=Keys.TAB, count=1):
        actions = ActionChains(self.driver)
        for _ in range(count):
            actions = actions.send_keys(key)
        actions.perform()

    # ==========================================================================
    def mouse_action_click(self, e, x=0, y=0):
        actions = ActionChains(self.driver)
        actions.move_to_element_with_offset(e, x, y)
        actions.click()
        actions.perform()

    # ==========================================================================
    def safe_click(self, e):
        # selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted
        try:
            e.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", e)

    # ==========================================================================
    def send_keys(self, e, keys):
        e.send_keys(keys)

    # ==========================================================================
    @staticmethod
    def get_download_path():
        """Returns the default downloads path for linux or windows"""
        if os.name == 'nt':
            import winreg
            sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
            downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                location = winreg.QueryValueEx(key, downloads_guid)[0]
            return location
        else:
            return os.path.join(os.path.expanduser('~'), 'downloads')

    # ==========================================================================
    def alert_action(self, action='accept', timeout=3):
        try:
            WebDriverWait(self.driver, timeout).until(EC.alert_is_present(),
                          'Timed out waiting for alert')
            alert = self.driver.switch_to.alert
            if action == 'accept':
                alert.accept()
                self.logger.info("alert accepted")
            else:
                alert.dismiss()
                self.logger.info("alert dissmissed")
        except TimeoutException:
            self.logger.info(f"no alert with timeout {timeout}")

    # ==========================================================================
    def close_all_popups(self):
        # 팝업창이 여러개 일때 닫기
        main = self.driver.window_handles
        self.main_handle = main_handle = main[0]
        for handle in main:
            if handle != main_handle:
                self.driver.switch_to.window(handle)
                self.driver.close()
        self.driver.switch_to.window(main_handle)

    # ==========================================================================
    def switch_to_window(self, index=1):
        # 해당 n번째 (1부터 시작) 팝업창으로 스위칭
        main = self.driver.window_handles
        self.main_handle = main_handle = main[0]
        for i, handle in enumerate(main):
            if handle == main_handle:
                continue
            if i == index:
                self.driver.switch_to.window(handle)
                break

    # ==========================================================================
    def switch_to_main_window(self):
        if self.main_handle is not None:
            self.driver.switch_to.window(self.main_handle)

    # ==========================================================================
    def scroll_by(self, x=0, y=0):
        if x > 0:
            x = f'+{x}'
        if y > 0:
            y = f'+{y}'
        self.driver.execute_script(f"scrollBy({x},{y});")

    # ==========================================================================
    def switch_to_iframe(self, xpath):
        self.switch_from_iframe()
        iframe = self.get_by_xpath(xpath)
        self.driver.switch_to.frame(iframe)

    # ==========================================================================
    def switch_to_iframe_by_name(self, iframe):
        self.switch_from_iframe()
        self.driver.switch_to.frame(iframe)

    # ==========================================================================
    def switch_from_iframe(self):
        self.driver.switch_to.default_content()

    # ==========================================================================
    def select_by_visible_text(self, xpath, text):
        e = self.get_by_xpath(xpath)
        s = Select(e)
        s.select_by_visible_text(text)

    # ==========================================================================
    def select_by_value(self, xpath, value):
        e = self.get_by_xpath(xpath)
        s = Select(e)
        s.select_by_value(value)

    # ==========================================================================
    def select_by_index(self, xpath, index):
        e = self.get_by_xpath(xpath)
        s = Select(e)
        s.select_by_index(index)

    # ==========================================================================
    @staticmethod
    def safe_download_move(glob_f, target_f, timeout=10):
        is_found = False
        for _ in range(timeout):
            if is_found:
                break
            for f in glob.glob(glob_f):
                # 저장하던 중일 수 있으므로 약간 기다림
                time.sleep(0.5)
                shutil.move(f, target_f)
                is_found = True
                break
            time.sleep(1)
        if not is_found:
            raise RuntimeError(f'safe_download_move: Cannot download file "{target_f}"')

    # ==========================================================================
    def xls_to_csv(self, xls_f, csv_f, num_headers=1, is_append=False):
        self.logger.debug(f'xls_to_csv: {xls_f} => {csv_f}')
        if not os.path.exists(xls_f):
            raise IOError(f'Cannot read Excel file "{xls_f}"')
        mode = 'a' if is_append else 'w'
        with open(csv_f, mode, encoding='utf-8') as ofp:
            c = csv.writer(ofp, lineterminator='\n')
            wb = xlrd.open_workbook(xls_f)
            ws = wb.sheet_by_index(0)
            for r_ndx in range(num_headers, ws.nrows):  # exclude header
                row = []
                for c_ndx in range(ws.ncols):
                    v = ws.cell(r_ndx, c_ndx).value
                    if not v:
                        v = ''
                    row.append(v)
                c.writerow(row)

    # ==========================================================================
    def new_tab(self, url):
        self.driver.execute_script(f'window.open("{url}","_blank");')

    # ==========================================================================
    def close_tab(self):
        self.driver.execute_script(f'window.close();')

    # ==========================================================================
    def start(self):
        raise NotImplementedError('Inherited Object must have start() method')


