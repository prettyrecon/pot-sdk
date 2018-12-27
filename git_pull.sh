#!/bin/bash

LC_ALL=C git reset --hard origin/master
LC_ALL=C git pull | tee dirty.txt | grep "Already up to date"
if [ $? -eq 0 ];then
	echo "Noting changed!"
	rm -f dirty.txt
	exit 1
else
	echo "Something changed!"
	cat dirty.txt
	exit 0
fi
