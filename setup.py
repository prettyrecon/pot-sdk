
import pip
import unittest
from setuptools import setup

pip_major_version = int(pip.__version__.split(".")[0])
if pip_major_version >= 20:
    from pip._internal.req import parse_requirements
    from pip._internal.network.session import PipSession
elif pip_major_version >= 10:
    from pip._internal.req import parse_requirements
    from pip._internal.download import PipSession
else:
    from pip.req import parse_requirements
    from pip.download import PipSession


################################################################################
def my_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('alabs.ppm',
                                      pattern='test*.py')
    return test_suite


################################################################################
# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("alabs\\ppm\\requirements.txt", session=PipSession())
#reqs = [str(ir.req) for ir in install_reqs]
reqs = list()
for ir in install_reqs:
    if hasattr(ir, 'req'):
        req = ir.req
    elif hasattr(ir, 'requirement'):
        req = ir.requirement
    else:
        raise LookupError('Cannot get requirement')
    reqs.append(str(req))
reqs.extend([])

setup(
    name='alabs.ppm',
    test_suite='setup.my_test_suite',
    packages=[
        'alabs','alabs.ppm','alabs.ppm.tests','alabs.ppm.pypiuploader'
    ],
    version='3.325.2420',
    description='ARGOS-LABS Module Manager',
    author='Jerry Chae',
    author_email='mcchae@argos-labs.com',
    url='https://www.argos-labs.com',
    license='ARGOS-LABS Proprietary License',
    keywords=['rpa', 'robot', 'module', 'manager', 'alabs', 'ppm'],
    platforms=['Mac', 'Windows', 'Linux'],
    install_requires=reqs,
    python_requires='>=3.6',
    package_data={'alabs.ppm': ['icon.*', 'setup.yaml', 'dumpspec.json']},
    zip_safe=False,
    classifiers=[
        'Build :: Date :: 2021-03-26 00:20',
        'Build :: Method :: alabs.ppm',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Change :: Log :: Add Manifest',
        'Topic :: Change :: Log :: Add input_group, input_method for plugin argument input attributes',
        'Topic :: Change :: Log :: Unittest for Linux',
        'Topic :: Change :: Log :: Unittest for Mac',
        'Topic :: Change :: Log :: Unittest for Windows',
        'Topic :: RPA',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': [
            'alabs.ppm=alabs.ppm:main',
        ],
    },
    include_package_data=True,
)
