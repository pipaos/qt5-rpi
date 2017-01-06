#!/bin/bash
#
#  Build and package everything in 2 separate steps: native and croos
#
#  buildall < cross | native>
#
# TODO: We might want to build the debug version of QT5 to diagnose problems
#
# ./qt5-build purge --yes > $logfile 2>&1
# ./qt5-build compile qt5 cross debug --baptize --yes >> $logfile 2>&1
#
#

if [ "$1" == "cross" ]; then
    # takes about 1 hour on a 8 CPU 2GHz host
    logfile="qt5-buildall-cross.log"
    echo "Cross compilation of QT5 and Webengine"
    echo "Follow progress at $logfile ..."
    ./qt5-build purge --yes > $logfile 2>&1
    ./qt5-build compile qt5 cross release --baptize --yes >> $logfile 2>&1
    ./qt5-build compile webengine release --yes >> $logfile 2>&1
    ./qt5-build package qt5 >> $logfile 2>&1
    ./qt5-build package webengine >> $logfile 2>&1
    ./qt5-build package cross-tools >> $logfile 2>&1
    exit 0
else if [ "$1" == "native" ]; then
	 # takes about 1.5 hours on a 8 CPU 2GHz host
	 logfile="qt5-buildall-native.log"
	 echo "Native compilation of QT5 core tools"
	 echo "Follow progress at $logfile ..."
	 ./qt5-build purge --yes > $logfile 2>&1
	 ./qt5-build compile qt5 native release --core-tools --yes >> $logfile 2>&1
	 ./qt5-build package native-tools >> $logfile 2>&1
	 exit 0
     else
	 echo "unrecognized build mode - please use native or cross"
	 exit 1
     fi
fi
