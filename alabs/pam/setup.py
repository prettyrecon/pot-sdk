
import unittest
from setuptools import setup
try: # for pip >= 10
    from pip._internal.req import parse_requirements
    from pip._internal.download import PipSession
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements
    from pip.download import PipSession


################################################################################
def my_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('alabs.pam',
                                      pattern='test*.py')
    return test_suite


################################################################################
# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("alabs\\pam\\requirements.txt", session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='alabs.pam',
    test_suite='setup.my_test_suite',
    packages=[
        'alabs','alabs.pam','alabs.pam.tests.scenarios','alabs.pam.tests.scenarios.MacOS','alabs.pam.tests.scenarios.MacOS.LA-Scenario0010','alabs.pam.variable_manager','alabs.pam.variable_manager.tests','alabs.pam.variable_manager.rest','alabs.pam.apps','alabs.pam.apps.variables_manager','alabs.pam.apps.bot_store_handler','alabs.pam.apps.pam_manager','alabs.pam.rpa','alabs.pam.rpa.desktop','alabs.pam.rpa.desktop.execute_process','alabs.pam.rpa.desktop.execute_process.ios','alabs.pam.rpa.desktop.execute_process.ios.tests','alabs.pam.rpa.desktop.execute_process.tests','alabs.pam.rpa.desktop.compare_text','alabs.pam.rpa.desktop.compare_text.linux','alabs.pam.rpa.desktop.compare_text.ios','alabs.pam.rpa.desktop.compare_text.tests','alabs.pam.rpa.desktop.stop_process','alabs.pam.rpa.desktop.stop_process.ios','alabs.pam.rpa.desktop.stop_process.ios.tests','alabs.pam.rpa.desktop.stop_process.tests','alabs.pam.rpa.desktop.screenshot','alabs.pam.rpa.desktop.screenshot.tests','alabs.pam.rpa.desktop.screenshot.ios','alabs.pam.rpa.desktop.screenshot.ios.tests','alabs.pam.rpa.desktop.screenshot.macos','alabs.pam.rpa.desktop.screenshot.linux','alabs.pam.rpa.desktop.select_window','alabs.pam.rpa.desktop.select_window.ios','alabs.pam.rpa.desktop.select_window.windows','alabs.pam.rpa.desktop.select_window.tests','alabs.pam.rpa.desktop.delete_file','alabs.pam.rpa.desktop.delete_file.tests','alabs.pam.rpa.desktop.delay','alabs.pam.rpa.desktop.delay.tests','alabs.pam.rpa.autogui','alabs.pam.rpa.autogui.type_text','alabs.pam.rpa.autogui.type_text.ios','alabs.pam.rpa.autogui.type_text.ios.tests','alabs.pam.rpa.autogui.type_text.linux','alabs.pam.rpa.autogui.type_text.macos','alabs.pam.rpa.autogui.type_text.tests','alabs.pam.rpa.autogui.locate_image','alabs.pam.rpa.autogui.locate_image.macos','alabs.pam.rpa.autogui.locate_image.linux','alabs.pam.rpa.autogui.locate_image.tests','alabs.pam.rpa.autogui.locate_image.ios','alabs.pam.rpa.autogui.locate_image.ios.tests','alabs.pam.rpa.autogui.send_shortcut','alabs.pam.rpa.autogui.send_shortcut.tests','alabs.pam.rpa.autogui.click','alabs.pam.rpa.autogui.click.linux','alabs.pam.rpa.autogui.click.ios','alabs.pam.rpa.autogui.click._tests','alabs.pam.rpa.autogui.screenshot','alabs.pam.rpa.autogui.screenshot.tests','alabs.pam.rpa.autogui.scroll','alabs.pam.rpa.autogui.scroll.tests','alabs.pam.rpa.autogui.scroll.ios','alabs.pam.rpa.autogui.scroll.linux','alabs.pam.rpa.autogui.scroll.macos','alabs.pam.rpa.autogui.dialogue','alabs.pam.rpa.autogui.dialogue.ios','alabs.pam.rpa.autogui.dialogue.linux','alabs.pam.rpa.autogui.dialogue.tests','alabs.pam.rpa.autogui.user_parameters','alabs.pam.rpa.autogui.user_parameters.linux','alabs.pam.rpa.autogui.user_parameters.ios','alabs.pam.rpa.autogui.user_parameters.tests','alabs.pam.rpa.autogui.find_image_location','alabs.pam.rpa.autogui.find_image_location.linux','alabs.pam.rpa.autogui.find_image_location.macos','alabs.pam.rpa.autogui.find_image_location.ios','alabs.pam.rpa.autogui.find_image_location.ios.tests','alabs.pam.rpa.autogui.find_image_location.tests','alabs.pam.rpa.autogui.touch','alabs.pam.rpa.autogui.touch.tests','alabs.pam.rpa.autogui.swipe','alabs.pam.rpa.autogui.swipe.tests'
    ],
    version='1.000.0',
    description='ARGOS-LABS RPA PYTHON PAM',
    author='Duk Kyu Lim',
    author_email='deokyu@argos-labs.com',
    url='https://www.argos-labs.com',
    license='ARGOS-LABS Proprietary License',
    keywords=['rpa', 'bot', 'pam', 'alabs'],
    platforms=['Windows'],
    install_requires=reqs,
    python_requires='>=3.6',
    package_data={'alabs.pam': ['icon.*', 'dumpspec.json',
                                'rpa/autogui/send_shortcut/*.yaml']},
    zip_safe=False,
    classifiers=[
        'Build :: Date :: 2019-12-31 13:39',
        'Build :: Method :: alabs.ppm',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Change :: Log :: Unittest for Windows',
        'Topic :: Python PAM',
        'Topic :: RPA',
    ],
    entry_points={
        'console_scripts': [
            'alabs.pam=alabs.pam:main',
        ],
    },
    include_package_data=True,
)
