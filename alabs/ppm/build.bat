@echo off
REM !/bin/bash

pip install PyYAML
set PYTHONPATH=..\..

python test_ppm.py
IF NOT %ERRORLEVEL% == 0 (
	echo "ppm test, build, upload ERROR!"
    goto errorExit
)

echo "ppm test, build, upload Success!"

: errorExit
