#
#  The MIT License (MIT)
#
#  Copyright (c) 2016-2017 Albert Casals - skarbat@gmail.com
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
#
#  compiler.py
#
#  Compiler classes to build QT5 and Webengine
#
#  See the README file for details.
#

import os
from builder import Builder

class CompilerQt5(Builder):
    
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

    def configure(self, core_tools=False):
        if core_tools:
            configure_opts=self.config['configure_core_tools']
        else:
            configure_opts=self.config['configure_release'] if self.release else self.config['configure_debug']

        if self.cross:
            command='cd {} && ./configure {}'.format(self.config['sources_directory'], configure_opts)
        else:
            command='xsysroot -x "/bin/bash -c \'cd /tmp/{} && ./configure {}\'"'.format(
                self.config['qt5_clone_dir'], configure_opts)

        if self.dry_run:
            print '>>>', command
            return True

        rc = os.system(command)
        return os.WEXITSTATUS(rc) == 0

    def make(self):
        if self.cross:
            command='cd {sources_directory} && make -j {num_cpus}'.format(**self.config)
        else:
            command='xsysroot -x "/bin/bash -c \'cd /tmp/{qt5_clone_dir} && make -j {num_cpus}\'"'.format(**self.config)

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
            'HostBinaries = {qt5_install_prefix}/{qt5_cross_binaries}\n'.format(**self.config)

        if self.cross:
            command='cd {sources_directory} && sudo make install && ' \
                'sudo mv -fv {cross_install_dir}/bin {cross_install_dir}/{qt5_cross_binaries}'.format(**self.config)
        else:
            command='xsysroot -x "/bin/bash -c \'cd /tmp/{qt5_clone_dir} && make install\'"'.format(**self.config)

        if self.dry_run:
            print '>>>', command
            return True

        rc = os.system(command)
        if not rc and self.cross:
            # TODO: Make this simpler
            qtconfig_file='{qt5_cross_qt_conf}'.format(**self.config)
            qtconfig_temp='qt.conf'
            with open (qtconfig_temp, 'w') as f:
                f.write(qtconfig)

            os.system('sudo cp -fv qt.conf {qt5_cross_qt_conf}'.format(**self.config))

        return os.WEXITSTATUS(rc) == 0


class CompilerWebengine(Builder):

    def apply_patches(self):
        patches_dir='patches/qtwebengine'
        if os.path.isdir('patches/qtwebengine'):
            print '>>> applying patches'
            cmd='cp -frv {}/* {}/qtwebengine'.format(patches_dir, self.config['sources_directory'])
            if self.dry_run:
                print '>>>', cmd
                return True
            else:
                return os.WEXITSTATUS(os.system(cmd))

    def qmake(self):
        qmake_cmd='{}; cd {}/qtwebengine && qmake ' \
            'WEBENGINE_CONFIG+=use_proprietary_codecs CONFIG+={}'.format(
                self.config['qmake_env'],
                self.config['sources_directory'],
                'release' if self.release else 'debug')

        if self.dry_run:
            print 'qmake >>>', qmake_cmd
            return True
        else:
            return os.WEXITSTATUS(os.system(qmake_cmd))

    def make(self):
        make_cmd='{qmake_env}; cd {sources_directory}/qtwebengine && make -j {num_cpus}'.format(**self.config)
        if self.dry_run:
            print 'make >>>', make_cmd
            return True
        else:
            return os.WEXITSTATUS(os.system(make_cmd))

    def install(self):
        install_cmd='{qmake_env}; cd {sources_directory}/qtwebengine && sudo make install'.format(**self.config)
        if self.dry_run:
            print 'install >>>', install_cmd
            return True
        else:
            return os.WEXITSTATUS(os.system(install_cmd))
