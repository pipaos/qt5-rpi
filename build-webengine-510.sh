#!/bin/bash
#
# Build QT Webengine 5.10
#
# This quick script collects the steps that I managed to pull together
# in order to cross build webengine separately from QT5 base.
#
# You will need:
#
# A "pipaos-devel" cross sysroot with libqt5all and libqt5all-dev 5.9 installed.
# On the host, libqt5all-cross-tools 5.9, and g++-multilib packages.
#

xsysroot_profile="pipa5"
install_deps=1

function sysexec()
{
    xsysroot -p $xsysroot_profile -x "$1"
}


if [ "$install_deps" == "1" ]; then

    # install dependencies on the sysroot image
    DEPS="libqt5all-dev libicu-dev libasound-dev libdbus-1-dev libfontconfig1-dev libjpeg62-turbo-dev libnss3-dev libsystemd-dev"
    sysexec "apt-get install -y $DEPS"

    # fix relative symlinks otherwise the linker fails traversing the sysroot paths
    sysexec "rm -fv /usr/lib/arm-linux-gnueabihf/libdl.so"
    sysexec "cp -fv /lib/arm-linux-gnueabihf/libdl.so.2 /usr/lib/arm-linux-gnueabihf/libdl.so"
    sysexec "rm -fv /usr/lib/arm-linux-gnueabihf/libm.so"
    sysexec "cp -fv /lib/arm-linux-gnueabihf/libm.so.6 /usr/lib/arm-linux-gnueabihf/libm.so"
    
    # The host packages below are due to a broken Webengine 5.10 build:
    # https://bugreports.qt.io/browse/QTBUG-65079?page=com.atlassian.jira.plugin.system.issuetabpanels%3Acomment-tabpanel&showAll=tru
    HOSTDEPS="libnss3-dev libpng-dev gcc-multilib g++-multilib"
    sudo apt-get install -y $HOSTDEPS
fi

# Clone and build QTQWebengine
rm -rf qtwebengine
git clone https://code.qt.io/qt/qtwebengine.git
cd qtwebengine
git checkout 5.10
git submodule update --init

# More subtle hacks for a currently broken build
export PKG_CONFIG=/tmp/pipa5/usr/lib/arm-linux-gnueabihf/pkgconfig
export PKG_CONFIG_PATH=/tmp/pipa5/usr/lib/arm-linux-gnueabihf/pkgconfig

#
# During linkge, a manual hack is needed:
# When the link stage fails with: undefined reference to InitializeOneOff()
#
# *  edit the source src/3rdparty/chromium/ui/ozone/common/gl_ozone_egl.cc
#    and remove references to function above, forcing a False return to, as well as ShutdownOneOff()
#    https://forum.qt.io/topic/85904/cannot-cross-compile-qt-5-10-0-for-raspberry-pi/6
#
# *  run "make" again
#
# Note that this version is currently buggy and you'll get graphical artifacts on complex websites
#
qmake WEBENGINE_CONFIG+=use_proprietary_codecs WEBENGINE_CONFIG+=embedded_build CONFIG+=release QMAKE_LFLAGS+="-lsystemd"
make -j 8
