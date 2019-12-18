@echo off
REM !/bin/bash
REM %USERPROFILE%.argos-rpa.conf 파일 확인 및 다음과 같이 확인
REM repository:
REM   url: http://10.211.55.2:48080

pip install PyYAML
set PYTHONPATH=..\..

REM python test_ppm.py
python __main__.py --pr-user mcchae@gmail.com --pr-user-pass ghkd67vv --venv upload

IF NOT %ERRORLEVEL% == 0 (
	echo "ppm test, build, upload ERROR!"
    goto errorExit
)

echo "ppm test, build, upload Success!"

: errorExit
