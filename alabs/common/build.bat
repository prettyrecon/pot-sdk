@echo off
REM !/bin/bash

set VB=-vvv

for /f %%i in ('alabs.apm get repository') do set REP=%%i
for /f %%i in ('alabs.apm get trusted-host') do set TH=%%i

pip install -U alabs.apm -i %REP% --trusted-host %TH%

REM # clear
alabs.apm --venv clear-all

REM test
alabs.apm --venv %VB% test
IF NOT %ERRORLEVEL% == 0 (
	echo "test have error"
    goto errorExit
)

REM # build
alabs.apm --venv %VB% build
IF NOT %ERRORLEVEL% == 0 (
	echo "build have error"
    goto errorExit
)

REM # upload
alabs.apm --venv %VB% upload
IF NOT %ERRORLEVEL% == 0 (
	echo "upload have error"
    goto errorExit
)

REM # clear
alabs.apm --venv clear-all

echo "Build all success!"

: errorExit