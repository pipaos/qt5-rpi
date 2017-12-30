#!/bin/bash
#
# Build QT Webengine 5.9
#
# This quick script collects the steps that I managed to pull together
# in order to cross build webengine separately from QT5 base.
#
# You will need:
#
# A "pipaos-devel" cross sysroot with libqt5all and libqt5all-dev 5.9 installed.
# On the host, libqt5all-cross-tools 5.9, and g++-multilib packages.
#

xsysroot_profile=pipa5

function sysexec()
{
    xsysroot -p $xsysroot_profile -x "$1"
}


# install dependencies on the sysroot image
DEPS="libqt5all-dev libicu-dev libasound-dev libdbus-1-dev libfontconfig1-dev libjpeg62-turbo-dev libsystemd-dev"
sysexec "apt-get install -y $DEPS"

# fix relative symlinks otherwise the linker fails traversing the sysroot paths
sysexec "rm -fv /usr/lib/arm-linux-gnueabihf/libdl.so"
sysexec "cp -fv /lib/arm-linux-gnueabihf/libdl.so.2 /usr/lib/arm-linux-gnueabihf/libdl.so"
sysexec "rm -fv /usr/lib/arm-linux-gnueabihf/libm.so"
sysexec "cp -fv /lib/arm-linux-gnueabihf/libm.so.6 /usr/lib/arm-linux-gnueabihf/libm.so"

# We build the clone from github, not the official QT repositories
# Fixes this problem: https://bugreports.qt.io/browse/QTBUG-57268
rm -rf qtwebengine
git clone https://code.qt.io/qt/qtwebengine.git -b 5.9.4
cd qtwebengine
git submodule update --init

# Note: enabling system icu and ffmpeg breaks the build,
# also installing these libraries confuses ninja and breaks the build.
# 
# WEBENGINE_CONFIG+=use_system_icu
# WEBENGINE_CONFIG+=use_system_ffmpeg

# FIXME: pkg-config in cross builds is still problematic
export PKG_CONFIG=$(xsysroot -p $xsysroot_profile -q sysroot)/usr/lib/arm-linux-gnueabihf/pkgconfig
export PKG_CONFIG_PATH=$PKG_CONFIG

# We have to force the paths to locate the shared libraries (qmake $ORIG mysterious macro)
QTLIBS="/usr/local/qt5/lib"
qmake WEBENGINE_CONFIG+=use_proprietary_codecs WEBENGINE_CONFIG+=embedded_build "QMAKE_LFLAGS+=-Wl,-rpath,$QTLIBS"

# If the link stage fails with "undefined reference to `sd_listen_fds'"
# Hack src/core/Makefile.core_module to add "-lsystemd" into the LIBS macro
# Then run make and sudo make install manually.

# Consider using -j X, as it can takes ages
# 3 hours to link the liqt5webengine.so object alone on a single core host!
make -j 8
