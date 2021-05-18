#!/bin/bash

# File downloaded from https://www.bocop.org/download/
# Distributed under EPL licence

## shell script for Bocop build
## Pierre Martinon, Inria
## 2019

## set build folder
if ! [ -d build ]; then
  mkdir build
fi
cd build

## default cmake options
NLPPATH=${BOCOPPATH:-"/home/prax/Software/bin/Bocop-2.2.0-linux-src/"}
platform=""
buildtype="Release" 

## set specific cmake options
#if [[ "$(uname -s)" =~ "MSYS" ]]; then
#  platform="-G \"MSYS Makefiles\" "
#fi
KERNEL=`uname -s`
case "$KERNEL" in
*"MSYS"*) platform="-G \"MSYS Makefiles\" ";;
esac

while getopts d option
do
case "${option}" in
d) buildtype="Debug";;
esac
done

## launch cmake, make and go back to problem folder
cmake ${platform} -DCMAKE_BUILD_TYPE=${buildtype} ${NLPPATH}
make -j
cd -
