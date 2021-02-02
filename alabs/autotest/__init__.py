"""
====================================
 :mod:alabs.autotest
====================================
.. moduleauthor:: Jerry Chae <mcchae@argos-labs.com>
.. note:: ARGOS-LABS License

Description
===========
automatic testing for plugins
"""
# Authors
# ===========
#
# * Jerry Chae
#
# Change Log
# --------
#
#  * [2020/01/04]
#     - demploy to alabs.autotest
#  * [2020/12/14]
#     - Starting

################################################################################
import os
import sys
import yaml
import json
import time
import shutil
import argparse
import schedule
import datetime
import traceback
import subprocess
import pathlib
from io import StringIO
from tempfile import gettempdir, TemporaryFile
from alabs.common.util.vvlogger import get_logger
from alabs.common.util.vvargs import ModuleContext, func_log, \
    ArgsError, ArgsExit, get_icon_path


################################################################################
AT = None


################################################################################
class AutoTest(object):
    # ==========================================================================
    @staticmethod
    def conf_substitute(conf_s):
        conf_s = conf_s.replace('{{gettempdir}}', gettempdir())
        conf_s = conf_s.replace('{{home}}', str(pathlib.Path.home()))
        return conf_s

    # ==========================================================================
    def __init__(self, args):
        conf_f = args.conf
        _filter = args.filter
        if not _filter:
            _filter = list()
        if getattr(sys, 'frozen', False):
            g_dir = os.path.abspath(sys._MEIPASS)
            c_dir = os.path.abspath(os.path.dirname(sys.executable))
            # print('pdir=%s, cdir=%s' % (g_dir, c_dir))
        else:
            g_dir = c_dir = os.path.abspath(os.path.dirname(__file__))
        self.g_dir = g_dir
        if not conf_f:
            conf_f = os.path.join(g_dir, 'autotest.yaml')
        if not os.path.exists(conf_f):
            raise IOError(f'Cannot read conf file "{conf_f}"')
        with open(conf_f, encoding='utf-8') as ifp:
            conf_s = ifp.read()
        conf_s = self.conf_substitute(conf_s)
        conf_sio = StringIO(conf_s)
        self.conf = yaml.load(conf_sio, yaml.FullLoader)
        self.filter = _filter
        self.tee = args.tee
        # for internal
        self.logger = get_logger(self.conf['environment']['log'])
        self.logger.info('Starting AutoTest object...')
        self.report = None
        self._init_report()

    # ==========================================================================
    def _init_report(self):
        self.report = {
            'subject': 'Automatic Plugin Test',
            'contents': [],
            'summary': [],
        }

    # ==========================================================================
    def _summary(self, msg):
        msg = msg.strip()
        self.report['summary'].append(f'{msg}')

    # ==========================================================================
    def _error(self, msg):
        msg = msg.strip()
        if self.tee:
            sys.stderr.write('[ERROR]:' + msg + '\n')
        self.logger.error(msg)
        self.report['contents'].append(f'[{datetime.datetime.now().strftime("%Y%m%d %H%M%S")}] ERROR: {msg}')

    # ==========================================================================
    def _info(self, msg):
        msg = msg.strip()
        if self.tee:
            sys.stdout.write('[INFO]:' + msg + '\n')
        self.logger.info(msg)
        self.report['contents'].append(f'[{datetime.datetime.now().strftime("%Y%m%d %H%M%S")}] INFO: {msg}')

    # ==========================================================================
    def _debug(self, msg):
        msg = msg.strip()
        if self.tee:
            sys.stdout.write('[DEBUG]:' + msg + '\n')
        self.logger.debug(msg)
        self.report['contents'].append(f'[{datetime.datetime.now().strftime("%Y%m%d %H%M%S")}] DEBUG: {msg}')

    # ==========================================================================
    def _do_cmd(self, cmd):
        f_out = TemporaryFile()
        f_err = TemporaryFile()
        try:
            # print(os.environ.get('_OLD_VIRTUAL_PATH'))
            # print(os.environ.get('VIRTUAL_ENV'))
            # del os.environ['_OLD_VIRTUAL_PATH']
            # del os.environ['VIRTUAL_ENV']
            po = subprocess.Popen(cmd, stdout=f_out, stderr=f_err, env=os.environ)
            po.wait()
            rc = po.returncode
            f_out.seek(0)
            f_err.seek(0)
            s_out = f_out.read().decode()
            s_err = f_err.read().decode()
            if rc != 0:
                raise RuntimeError(f'Cmd="{" ".join(cmd)}" returns {rc}\n'
                                   f'stdout="{s_out}"\nstderr="{s_err}"')
            self._info(f'Cmd="{" ".join(cmd)}" returns {rc}\n'
                       f'stdout="{s_out}"\nstderr="{s_err}"')
            return s_out
        finally:
            f_out.close()
            f_err.close()

    # ==========================================================================
    def make_venv(self):
        # Error: Command '['C:\\Users\\mcchae\\autotest.venv\\Scripts\\python.exe',
        #   '-Im', 'ensurepip', '--upgrade', '--default-pip']' returned non-zero exit status 1
        # so use without-pip
        cmd = [
            self.conf['environment']['virtualenv']['py3'],
            '-m', 'venv',
            self.conf['environment']['virtualenv']['dir'],
            '--without-pip',
        ]
        self._do_cmd(cmd)

        venv_py = os.path.join(self.conf['environment']['virtualenv']['dir'],
                               'Scripts', 'python.exe')
        get_pip = os.path.join(self.g_dir, 'get-pip.py')
        cmd = [
            venv_py,
            get_pip
        ]
        self._do_cmd(cmd)

    # ==========================================================================
    def pip_install_plugin(self, plugin, version=None):
        venv_pip = os.path.join(self.conf['environment']['virtualenv']['dir'],
                                'Scripts', 'pip.exe')
        cmd = [
            venv_pip,
            'install',
            '-i', 'https://pypi-official.argos-labs.com/simple',
            plugin,
        ]
        if version:
            cmd.append(f'=={version}')
        self._do_cmd(cmd)

    # ==========================================================================
    def prepare_venv(self, is_clear=False):
        venv_dir = self.conf['environment']['virtualenv']['dir']
        if is_clear and os.path.exists(venv_dir):
            shutil.rmtree(venv_dir)
        # venv_py_f = os.path.join(venv_dir, 'Scripts', 'python.exe')
        if not os.path.exists(venv_dir):
            # making venv
            self.make_venv()
        self.pip_install_plugin(self.conf['report']['email']['plugin'])

    # ==========================================================================
    def do_test(self, test):
        s_ts = datetime.datetime.now()
        try:
            self._info(f'\n{"="*100}\nStart testing {test["name"]}')
            self.pip_install_plugin(test['plugin'])
            cmd = test['cmd']
            cmd[0] = os.path.join(self.conf['environment']['virtualenv']['dir'],
                                  'Scripts', cmd[0])
            stdout = self._do_cmd(cmd)
            stdout_json = test.get('stdout_json', False)
            if stdout_json:
                js = json.loads(stdout)
            br = eval(test['assert_true'], globals(), locals())
            if br:
                self._info(f'Checking for result "{test["assert_true"]}" is OK')
                self._summary(f'[{test["plugin"]}] {test["name"]} passed')
            else:
                self._info(f'Checking for result "{test["assert_true"]}" is NOK!')
                self._summary(f'[{test["plugin"]}] {test["name"]} NOT passed')
            return br
        except Exception as err:
            _exc_info = sys.exc_info()
            _out = traceback.format_exception(*_exc_info)
            del _exc_info
            self._error('implicitly_wait Error: %s\n' % str(err))
            self._error('%s\n' % ''.join(_out))
            self._summary(f'[{test["plugin"]}] {test["name"]} got Exception!')
            return False
        finally:
            e_ts = datetime.datetime.now()
            self._info(f'\nTesting ended and it takes {e_ts - s_ts}')

    # ==========================================================================
    def email_report(self, s_ts, e_ts, succ_cnt, fail_cnt):
        total_cnt = succ_cnt + fail_cnt
        email_f = os.path.join(gettempdir(), 'autotest.report.txt')
        with open(email_f, 'w', encoding='utf-8') as ofp:
            ofp.write(f'This testing started at {s_ts} and ended at {e_ts},\n'
                      f'it took {e_ts - s_ts}\n\n')
            ofp.write(f'Total {total_cnt} plugins and falied {fail_cnt}\n\n\n')
            for i, s in enumerate(self.report['summary']):
                ofp.write(f'[{i+1:04}/{total_cnt}] {s}\n')
            ofp.write(f'\n\n\n{"*" * 100}\n')
            ofp.write('\n'.join(self.report['contents']))
        cmd = [
            os.path.join(self.conf['environment']['virtualenv']['dir'],
                         'Scripts', self.conf['report']['email']['plugin']),
            self.conf['report']['email']['server'],
            self.conf['report']['email']['user'],
            self.conf['report']['email']['passwd'],
            f'[{s_ts.strftime("%Y%m%d %H%M%S")}~{e_ts.strftime("%Y%m%d %H%M%S")}]'
            f' {self.report["subject"]} {fail_cnt} fails out of {total_cnt}',
            '--body-file', email_f,
        ]
        for i, to in enumerate(self.conf['report']['email']['to']):
            if i < 1:
                cmd.extend(['--to', to])
            # else:
            #     cmd.extend(['--cc', to])
        self._do_cmd(cmd)

    # ==========================================================================
    def do_tests(self):
        s_ts = datetime.datetime.now()
        self._init_report()
        self.prepare_venv()
        succ_cnt = fail_cnt = 0
        if self.filter:
            tests = list()
            for t in self.conf.get('tests', []):
                b_found = False
                for f in self.filter:
                    if t['name'].find(f) >= 0:
                        b_found = True
                        break
                if b_found:
                    tests.append(t)
        else:
            tests = self.conf.get('tests', [])
        for test in tests:
            br = self.do_test(test)
            if br:
                succ_cnt += 1
            else:
                fail_cnt += 1
        e_ts = datetime.datetime.now()
        self.email_report(s_ts, e_ts, succ_cnt, fail_cnt)


################################################################################
def do_schedule():
    global AT
    AT.do_tests()


################################################################################
def do_schedule_new_env():
    global AT
    AT.prepare_venv(is_clear=True)
    AT.do_tests()


################################################################################
def _main(*args):
    with ModuleContext(
        owner='ARGOS-LABS',
        group='alabs',
        version='1.0',
        platform=['windows', 'darwin', 'linux'],
        output_type='text',
        display_name='Argos Icon',
        icon_path=get_icon_path(__file__),
        description='alabs.autotest util for automatic plugin testing',
    ) as mcxt:
        mcxt.add_argument('--conf', '-c',
                          help='set config file')
        mcxt.add_argument('--start', '-s', action='store_true',
                          help='If this flag is set just run starting and exit')
        mcxt.add_argument('--filter', '-f', action='append',
                          help='Only matching contains this string for the name')
        mcxt.add_argument('--clear-venv', action='store_true',
                          help='If this flag is set clear VirtualEnv before testing')
        mcxt.add_argument('--tee', action='store_true',
                          help='If this flag is set print out to stdout too')
        argspec = mcxt.parse_args(args)
        at = AutoTest(argspec)
        if argspec.clear_venv:
            at.prepare_venv(is_clear=True)
        if argspec.start:
            at.do_tests()
            return 0
        global AT
        AT = at
        for sch in at.conf.get('schedule', []):
            if sch['before_clear']:
                schedule.every().day.at(sch['at']).do(do_schedule_new_env)
            else:
                schedule.every().day.at(sch['at']).do(do_schedule)
        while True:
            schedule.run_pending()
            time.sleep(1)
        return 0


################################################################################
def main(*args):
    try:
        return _main(*args)
    except ArgsError as err:
        sys.stderr.write('Error: %s\nPlease -h to print help\n' % str(err))
    except ArgsExit as _:
        pass

