#
#  Builder class to wrap up all the build stages
#

import os
import sys
import time
import platform
import multiprocessing
import json
import pprint
import xsysroot

class Builder():

    def __init__(self, config_file='qt5-configuration.json', cross=True, release=True, dry_run=True):
        self.config = json.loads(open(config_file, 'r').read())
        self.sysroot = xsysroot.XSysroot(profile=self.config['xsysroot_profile'])
        self.cross=cross
        self.release=release
        self.dry_run=dry_run
        self._complete_config()

    def _complete_config(self):
        self.config['sysroot'] = self.sysroot.query('sysroot')
        self.config['systmp'] = self.sysroot.query('tmp')
        self.config['num_cpus'] = multiprocessing.cpu_count()
        self.config['configure_release'] = self.config['configure_release'].format(**self.config)
        self.config['configure_debug'] = self.config['configure_debug'].format(**self.config)
        self.config['sources_directory'] ='{}/{}'.format(self.sysroot.query('tmp'), self.config['qt5_clone_dir'])
        self.config['cross_install_dir']='{}/{}'.format(self.sysroot.query('sysroot'), self.config['qt5_install_prefix'])
        self.config['qt5_cross_qt_conf']='{sysroot}/{qt5_install_prefix}/{qt5_cross_binaries}/qt.conf'.format(**self.config)
        self.host_numcpus=multiprocessing.cpu_count()

    def are_sources_cloned(self):
        return os.path.isdir(self.config['sources_directory'])

    def is_qt5_installed(self):
        return os.path.isdir(self.config['cross_install_dir'])

    def are_cross_tools_built(self):
        x64bins='{cross_install_dir}/{qt5_cross_binaries}'.format(**self.config)
        return os.path.isdir(x64bins)

    def dump_configuration(self):
        pprint.pprint(self.config, indent=2)

    def status(self):
        print 'sysroot mounted:', self.sysroot.is_mounted()
        print 'QT5 sources cloned:', self.are_sources_cloned()
        print 'QT5 installed:', self.is_qt5_installed()
        print 'QT5 cross tools built:', self.are_cross_tools_built()


class BuilderQt5(Builder):
    
    def clone_repos(self):
        if self.are_sources_cloned():
            print 'QT5 sources already cloned, continuing'
            return True

        git_command = 'git clone --branch={qt5_version} {qt5_repo_url} {sources_directory}'.format(**self.config)
        init_command='cd {sources_directory} ; perl ./init-repository'.format(**self.config)

        if self.dry_run:
            print '>>> ', git_command
            print '>>> ', init_command
            return True

        if os.system(git_command):
            print 'Error cloning sources'
            return False

        if os.system(init_command):
            print 'Error initializing repository'
            return False
        
        return True
        
    def baptize_image(self):
        '''
        Prepare the image for the first time.
        '''
        print '>>> baptizing image'
        if self.dry_run:
            return True

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
        command='apt-get install -y --no-install-recommends {sysroot_dependencies}'.format(**self.config)
        print '>>> installing sysroot dependencies'
        if self.dry_run:
            print '>>>', command
            return True

        if self.sysroot.execute('apt-get update'):
            return False

        if self.sysroot.execute(command):
            return False

        self._fix_qualified_paths()
        return True

    def _fix_qualified_paths(self):
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
        configure_opts=self.config['configure_release'] if self.release else self.config['configure_debug']
        if self.cross:
            command='cd {} && ./configure {}'.format(self.config['sources_directory'], configure_opts)
        else:
            command='xsysroot -x "cd /tmp/{} && ./configure {}"'.format(self.config['qt5_clone_dir'], configure_opts)

        if self.dry_run:
            print '>>>', command
            return True

        rc = os.system(command)
        return os.WEXITSTATUS(rc) == 0

    def make(self):
        if self.cross:
            command='cd {sources_directory} && make -j {num_cpus}'.format(**self.config)
        else:
            command='xsysroot -x "cd /tmp/{qt5_clone_dir} && make -j {num_cpus}"'.format(**self.config)

        if self.dry_run:
            print '>>>', command
            return True

        rc = os.system(command)
        return os.WEXITSTATUS(rc) == 0

    def install(self):
        # TODO create a qt.conf file
        qtconfig='[Paths]\n' \
            'Sysroot = {sysroot}\n' \
            'Prefix = {qt5_install_prefix}\n' \
            'HostPrefix= {sysroot}/{qt5_install_prefix}\n' \
            'Binaries = {qt5_cross_binaries}\n' \
            'HostBinaries = {qt5_cross_binaries}\n'.format(**self.config)

        if self.cross:
            command='cd {sources_directory} && sudo make install && ' \
                'sudo mv -fv {cross_install_dir}/bin {cross_install_dir}/{qt5_cross_binaries}'.format(**self.config)
        else:
            command='xsysroot -x "cd /tmp/{qt5_clone_dir} && make install'.format(**self.config)

        if self.dry_run:
            print '>>>', command
            print 'qtconfig >>>\n', qtconfig
            return True

        rc = os.system(command)
        if not rc and self.cross:
            # TODO: Make this simpler
            qtconfig_file='{qt5_cross_qt_conf}'.format(**self.config)
            qtconfig_temp='/tmp/qtconfig'
            with open (qtconfig_temp, 'w') as f:
                f.write(qtconfig)

            os.system('sudo cp -fv /tmp/qtconfig {qt5_cross_qt_conf}'.format(**self.config))

        return os.WEXITSTATUS(rc) == 0


class BuilderWebengine(Builder):

    def haw(self):
        pass
