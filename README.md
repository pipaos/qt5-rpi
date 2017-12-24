## QT5 RaspberryPI

This project builds QT5 and QT Webengine debian packages for the RaspberryPI.

### Requirements

You will need a powerful - 4 CPU or higher recommended-  Intel 64 bit computer with Debian Jessie.
The additional software needed on the host will be installed by running `./host-bootstrap.py`.

### Build

Build is separated in two stages.

Cross compilation of QT5, webengine and cross compilation tools: `buildall.sh cross`,
and native compilation of the core tools, for the RaspberryPI: `buildall.sh native`.

On completion, the `pkgs` directory will contain the Debian files to publish on the repository.

 * libqt5all.deb
 * libqtwebengine.deb
 * libqt5all-dev.deb
 * libqtwebengine-dev.deb
 * libqt5-native-tools.deb
 * libqt5-cross-tools.deb

### Development

QT5 and Webenegine apps can be compiled using the packages above, in two different ways: native or cross compiled.

#### Native compilation

You will need a RaspberryPI or a Rasbian based sysroot. Install the `-dev` packages on the sysroot along
with native tools package. Set your `PATH` to point to `/usr/local/qt5/bin`. You are now ready to build.

#### Cross compilation

You will need a Debian Jessie x64 system and a Rasbian based sysroot. Run the command `host-bootstrap` on the host.
Mount the sysroot image and install the `-dev` packages in it along with the cross tools package.
Set your `PATH` on the Host to reach qmake:

```
$ export PATH=$PATH:$(xsysroot -q sysroot)/usr/local/qt5/bin-x86-64`
```

You might need to set the correct path to the sysroot in the file `/usr/local/qt5/bin-x86-64/qt.conf`

You are now ready to cross build QT5 apps from the host.

### References

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

Albert Casals - 2016-2017
