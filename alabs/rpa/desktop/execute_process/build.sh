#!/bin/bash

VB=-vvv
#VB=

# for linux alabs.apm bin
export PATH=$PATH:/home/toor/.local/bin

REP=$(alabs.apm get repository)
TH=$(alabs.apm get trusted-host)

# install alabs.apm
pip3 install -U alabs.apm -i $REP --trusted-host $TH

# clear
alabs.apm --venv clear-all

# test
alabs.apm --venv $VB test
if [ $? -ne 0 ];then
	RC=$?
	echo "test failed!"
	exit $RC
fi

# build
alabs.apm --venv $VB build
if [ $? -ne 0 ];then
	RC=$?
	echo "build failed!"
	exit $RC
fi

# upload
alabs.apm --venv $VB upload
if [ $? -ne 0 ];then
	RC=$?
	echo "upload failed!"
	exit $RC
fi

# clear
alabs.apm --venv clear-all
