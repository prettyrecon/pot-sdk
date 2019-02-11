@echo off
REM !/bin/bash

pip install PyYAML
set PYTHONPATH=..\..

python test_apm.py
IF NOT %ERRORLEVEL% == 0 (
	echo "apm test, build, upload ERROR!"
    goto errorExit
)

echo "apm test, build, upload Success!"

: errorExit
