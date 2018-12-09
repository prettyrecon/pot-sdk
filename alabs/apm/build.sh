#!/bin/bash

pip install PyYAML
PYTHONPATH=../.. python3 test_apm.py
if [ $? -ne 0 ];then
	echo "apm test, build, upload ERROR!"
	exit 9
fi
echo "apm test, build, upload Success!"
exit 0
