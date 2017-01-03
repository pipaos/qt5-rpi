
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
        self.config['sources_directory'] ='{}/{}'.format(self.sysroot.query('tmp'), self.config['qt5_clone_dir'])
        self.host_numcpus=multiprocessing.cpu_count()

    def are_sources_cloned(self):
        return os.path.isdir(self.config['sources_directory'])
        
    def dump_configuration(self):
        pprint.pprint(self.config)


class BuilderQt5(Builder):
    
    def clone_repos(self):
        if self.are_sources_cloned():
            print 'QT5 sources already cloned'
            return True

        command = 'git clone --branch={} {} {}'.format(
            self.config['qt5_version'],
            self.config['qt5_repo_url'],
            self.config['sources_directory'])
        
        if os.system(command):
            print 'Error cloning sources'
            return False

        command='cd {} ; perl ./init-repository'.format(self.config['sources_directory'])
        if os.system(command):
            print 'Error initializing repository'
            return False
        
        return True
        
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

        return self.sysroot.mount()

    def install_dependencies(self):
        # Put the system up to date and install QT5 build dependencies
        # We might need more, for example TLS and further backends
        if self.sysroot.execute('apt-get update'):
            return False

        if self.sysroot.execute('apt-get install -y --no-install-recommends {}'.format(
                self.config['sysroot_dependencies'])):
            return False

        return True

    def fix_qualified_paths(self):
        # Fix relative symlinks to libdl and libm (so called fixQualifiedPaths in QT jargon)
        # TODO: Use readlink instead of hardcoded destination to .so versioned filename,
        #       but no big deal really. This is a development / builder box.
        self.sysroot.execute('rm -fv /usr/lib/arm-linux-gnueabihf/libdl.so')
        self.sysroot.execute('cp -fv /lib/arm-linux-gnueabihf/libdl.so.2 /usr/lib/arm-linux-gnueabihf/libdl.so')
        self.sysroot.execute('rm -fv /usr/lib/arm-linux-gnueabihf/libm.so')
        self.sysroot.execute('cp -fv /lib/arm-linux-gnueabihf/libm.so.6 /usr/lib/arm-linux-gnueabihf/libm.so')
        
        # Fix relative path for libudev library. This fixes plugging HID devices on-the-fly
        # The reason for this ugly patch is that "configure" seems to have lost the relative sysroot directory
        self.sysroot.execute('rm -fv /usr/lib/arm-linux-gnueabihf/libudev.so')
        os.system ('sudo ln -sfv {}/lib/arm-linux-gnueabihf/libudev.so.1.5.0 ' \
                   '{}/usr/lib/arm-linux-gnueabihf/libudev.so'.format(
                       self.sysroot.query('sysroot'),
                       self.sysroot.query('sysroot')))

    def configure(self):
        command='cd {} && ./configure {}'.format(self.config['sources_directory'], self.config['configure_release'])
        rc = os.system(command)
        return os.WEXITSTATUS(rc) == 0

    def make(self):
        command='cd {} && make -j {}'.format(self.config['sources_directory'], self.config['num_cpus'])
        rc = os.system(command)
        return os.WEXITSTATUS(rc) == 0

    def install(self):
        command='cd {} && sudo make install'.format(self.config['sources_directory'])
        rc = os.system(command)
        return os.WEXITSTATUS(rc) == 0
