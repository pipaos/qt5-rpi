
import os
import sys
import time
import platform
import multiprocessing
import json
import pprint
import xsysroot


class Builder():

    def __init__(self, config_file):
        self.config = json.loads(open(config_file, 'r').read())
        self.sysroot = xsysroot.XSysroot(profile=self.config['xsysroot_profile'])
        self._complete_config()

    def _complete_config(self):
        self.config['sysroot'] = self.sysroot.query('sysroot')
        self.config['systmp'] = self.sysroot.query('tmp')
        self.config['num_cpus'] = multiprocessing.cpu_count()
        self.config['configure_release'] = self.config['configure_release'].format(**self.config)
        self.config['configure_debug'] = self.config['configure_debug'].format(**self.config)
        self.host_numcpus=multiprocessing.cpu_count()

    def dump_configuration(self):
        pprint.pprint(self.config)



class BuilderQt5(Builder):
    
    def clone_repos():
        pass
        
    def baptize_image(self):
        '''
        Prepare the image for the first time.
        '''
        # make sure the image is not currently in use
        if self.sysroot.is_mounted():
            if not self.sysroot.umount():
                return False

        # renew the image so we start from clean
        if not self.sysroot.renew():
            return False
        else:
            # once renewed, expand it to grow in size, qt5 wouldn't fit
            self.sysroot.umount()
            if not self.sysroot.expand():
                print 'error expanding image size to {}'.format(picute.query('qcow_size'))
                return False

        return picute.mount()

    def fix_qualified_paths(self):
        # Fix relative symlinks to libdl and libm (so called fixQualifiedPaths in QT jargon)
        # TODO: Use readlink instead of hardcoded destination to .so versioned filename,
        #       but no big deal really. This is a development / builder box.
        picute.execute('rm -fv /usr/lib/arm-linux-gnueabihf/libdl.so')
        picute.execute('cp -fv /lib/arm-linux-gnueabihf/libdl.so.2 /usr/lib/arm-linux-gnueabihf/libdl.so')
        picute.execute('rm -fv /usr/lib/arm-linux-gnueabihf/libm.so')
        picute.execute('cp -fv /lib/arm-linux-gnueabihf/libm.so.6 /usr/lib/arm-linux-gnueabihf/libm.so')
        
        # Fix relative path for libudev library. This fixes plugging HID devices on-the-fly
        # The reason for this ugly patch is that "configure" seems to have lost the relative sysroot directory
        picute.execute('rm -fv /usr/lib/arm-linux-gnueabihf/libudev.so')
        os.system ('sudo ln -sfv {}/lib/arm-linux-gnueabihf/libudev.so.1.5.0 ' \
                   '{}/usr/lib/arm-linux-gnueabihf/libudev.so'.format(
                       picute.query('sysroot'),
                       picute.query('sysroot')))
                
    def install_dependencies(self):
        # Put the system up to date and install QT5 build dependencies
        # We might need more, for example TLS and further backends
        qt5_builddeps='libc6-dev libxcb1-dev libxcb-icccm4-dev libxcb-xfixes0-dev ' \
            'libxcb-image0-dev libxcb-keysyms1-dev libxcomposite-dev ' \
            'libxcb-sync0-dev libxcb-randr0-dev libx11-xcb-dev libxcb-render-util0-dev ' \
            'libxrender-dev libxext-dev libxcb-glx0-dev pkg-config ' \
            'libssl-dev libraspberrypi-dev libfreetype6-dev libxi-dev libcap-dev ' \
            'libwayland-dev libxkbcommon-dev build-essential git-core libfontconfig1-dev ' \
            'libasound2-dev libinput-dev libmtdev-dev libproxy-dev libdirectfb-dev ' \
            'libts-dev libudev-dev libxcb-xinerama0-dev ' \
            'libdbus-1-dev libicu-dev libglib2.0-dev '

        if picute.execute('apt-get update'):
            return False

        if picute.execute('apt-get install -y --no-install-recommends {}'.format(qt5_builddeps)):
                return False

        return True

