##QT5 RaspberryPI

This project builds QT5 and QT Webengine debian packages for the RaspberryPI.

###Requirements

You will need a powerful - 4 CPU or higher recommended-  Intel 64 bit computer with Debian Jessie.
The additional software needed will be installed by running `./host-bootstrap.py`.

###Build

Build everything with these commands:

```
$ ./qt5-build compile qt5 cross release --baptize
$ ./qt5-build compile webengine release
$ ./qt5-build package qt5
$ ./qt5-build package webengine
$ ./qt5-build package cross-tools
$ ./qt5-build purge
$ ./qt5-build compile qt5 native release --bare-tools
$ ./qt5-build package native-tools
```

Will build and debianize everything into the `pkgs` folder:

 * libqt5all.deb
 * libqtwebengine.deb
 * libqt5all-dev.deb
 * libqtwebengine-dev.deb
 * libqt5-tools-native.deb
 * libqt5-tools-x64.deb

###Development

QT5 and Webenegine apps can be compiled using the packages above, in 2 ways: native or cross compiled.

####Native compilation

You will need a RaspberryPI or a Rasbian based sysroot. Install the the `-dev` packages along
with libqt5-tools-native.deb. Set your `PATH` to point to `/usr/local/qt5/bin`. You are now ready to build.

####Cross compilation

You will need a Debian x64 system and a Rasbian based sysroot. Run the command `host-bootstrap`,
then setup the sysroot image. Install the `-dev` packages on the sysroot.
Then set your `PATH` on the Host to reach qmake:

```
$ export PATH=$PATH:$(xsysroot -q sysroot)/usr/local/qt5/bin-x86-64`
```

You are now ready to build from the host.

###References

 * https://github.com/CalumJEadie/part-ii-individual-project-dev/wiki/Project-Proposal-Research
 * https://wiki.qt.io/Building_Qt_5_from_Git
 * http://doc.qt.io/qt-5/embedded-linux.html#configuring-for-a-specific-device
 * http://wiki.qt.io/RaspberryPi2EGLFS
 * https://code.qt.io/cgit/qt
 * https://github.com/raspberrypi/tools.git
 * https://www.raspberrypi.org/documentation/linux/kernel/building.md
 * https://www.raspberrypi.org/blog/qt5-and-the-raspberry-pi/
 * http://www.ics.com/blog/building-qt-and-qtwayland-raspberry-pi
 * http://www.intestinate.com/pilfs/beyond.html#wayland
 * https://wiki.merproject.org/wiki/Community_Workspace/RaspberryPi
 * https://github.com/jorgen/yat
 * https://www.youtube.com/watch?v=AtYmJaqxuL4
 * https://aur.archlinux.org/cgit/aur.git/tree/PKGBUILD?h=qpi2
 * https://github.com/qtproject/qtwayland
 * http://www.chaosreigns.com/wayland/weston/
 * https://info-beamer.com/blog/raspberry-pi-hardware-video-scaler
 * https://forum.qt.io/topic/48223/webengine-raspberry-pi/2

Albert Casals, February 2016.
