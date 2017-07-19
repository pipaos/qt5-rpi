## Building the Debian Packages

This recipe is to build the complete set of packages to run and develop with QT5 and the Webengine.
Make sure you run them in the order outlined below.

### 1 Build core QT5 framework, Webengine, cross compilation tools:

 * ./buildall.sh cross
 * extract: libqt5all.deb, libqt5all-dev.deb, libqt5all-cross.deb, libqt5webengine.deb, liqt5webengine-dev.deb

### 2 Build QT5 framework with debug symbols:

 * ./qt5-build purge --yes
 * ./qt5-build compile qt5 cross debug --yes
 * ./qt5-build package qt5
 * extract: libqt5all-debug

```
 FIXME: debug build fails with message below.

parser.o tools/qdatetimeparser.cpp
tools/qdatetimeparser.cpp: In function ‘QString unquote(const QStringRef&)’:
tools/qdatetimeparser.cpp:342:1: internal compiler error: in push_minipool_fix, at config/arm/arm.c:14059
 }
  ^
  Please submit a full bug report,
```

### 3 Build QT5 RPi native compilation tools:

 * ./qt5-build purge --yes
 * ./qt5-build compile qt5 native release --core-tools --yes
 * ./qt5-build package native-tools
 * extract: libqt5all-native.deb
