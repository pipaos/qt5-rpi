##QT5 RaspberryPI

This project builds QT5 and QT Webengine debian packages for the RaspberryPI.

###Requirements

You will need a powerful - 4 CPU or higher recommended-  Intel 64 bit computer with Debian Jessie.
The additional software needed will be installed like this:

```
$ cd build
$ python host-bootstrap.py
```

###Prepare the image

Now get the pipaOS image ready, the so called sysroot.

```
$ mkdir ~/osimages ~/xtmp
$ cd ~/osimages && wget http://pipaos.mitako.eu/download/pipaos-lulo-xgui-4.4.img.gz
$ gunzip pipaos-lulo-xgui-4.4.img.gz
```

Copy the file `xsysroot.conf` to your home directory, then call `xsysroot -p picute -s`.

###Build

Picute.py will take hands, install QT5 dependencies on the sysroot and cross-build QT5 on it:

```
 $ ./buildme
```

All QT5 source code will be cloned into your `~/xtmp` folder, which sits on the host.
Once the build is complete, you will not want this anymore.

###Webengine

Once the buildme script has completed QT5, you can now build the Webengine.

```
$ python -u piwebengine.py picute > webengine.log 2>&1
```

Webengine build takes a long time. On successfeul completion it will have been installed inside the image.

###Cross compile your apps

On your Intel host computer, you'll need to mount the Picute image with `xsysroot -m`.
Then, add `/tmp/picute/usr/local/qt5.5/bin` to your path.

Now from your QT5 project sources, simply call `qmake` followed by `make`,
and it should build the app ready to run on Picute.

An alternative to having the Picute image on your Intel computer,
is to boot Picute on a networked RaspberryPI, and remote mount the sysroot, like this:

`
 $ mkdir /tmp/picute && sudo sshfs -o allow_other sysop@picute-ip-address:/ /tmp/picute
`

Pass `posys` for the network password.

##Webengine 5.7.1 dependencies

The following webengine dependencies can be installed manually:

 * http://httpredir.debian.org/debian/pool/main/f/ffmpeg/libavutil55_3.2-2~bpo8+2_armhf.deb
 * http://httpredir.debian.org/debian/pool/main/f/ffmpeg/libavcodec57_3.2-2~bpo8+2_armhf.deb
 * http://httpredir.debian.org/debian/pool/main/f/ffmpeg/libavformat57_3.2-2~bpo8+2_armhf.deb
 * http://httpredir.debian.org/debian/pool/main/libv/libvpx/libvpx4_1.6.0-2~bpo8+1_armhf.deb

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
