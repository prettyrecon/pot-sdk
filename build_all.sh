#!/bin/bash

# 0) pkg
pip3 install PyYAML

# 1) 쉘 스크립트가 있는 디레터리 위치 구함
WDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
echo "working directory for build_all is \"${WDIR}\""

# 2) 해당 디렉터리에서 재귀적으로 build.sh 를 구하여 $bf로 작업
for bf in $(find ${WDIR} -name "build.sh");do
    echo "building ${bf} ..."
    BDIR=$(dirname ${bf})
    python3 ${WDIR}/change_version.py -n ${BDIR}/setup.yaml
    pushd ${BDIR}
        bash build.sh
        if [ $? -ne 0 ];then
            echo "Error!!!"
            exit 9
        fi
    popd
    echo "building ${bf} done!"
done
echo "Build All is done!"
exit 0
