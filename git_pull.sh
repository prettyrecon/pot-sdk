#!/bin/bash

git pull | grep "Already up to date"
if [ $? -eq 0 ];then
	echo "Noting changed!"
	exit 1
else
	echo "Something changed!"
	exit 0
fi
