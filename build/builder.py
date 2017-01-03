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
#  builder.py
#
#  Builder class to wrap up settings and build stages
#
#  See the README file for details.
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

    def is_qt5_ready(self):
        '''
        Returns true if QT5 has been built and installed in the sysroot
        '''
        return self.are_sources_cloned() and self.is_qt5_installed() and self.are_cross_tools_built()

    def dump_configuration(self):
        pprint.pprint(self.config, indent=2)

    def status(self):
        print 'sysroot mounted:', self.sysroot.is_mounted()
        print 'QT5 sources cloned:', self.are_sources_cloned()
        print 'QT5 installed:', self.is_qt5_installed()
        print 'QT5 cross tools built:', self.are_cross_tools_built()

    def purge(self):
        clean_sources='sudo rm -rf {sources_directory}'.format(**self.config)
        clean_binaries='sudo rm -rf {cross_install_dir}'.format(**self.config)

        print '>>>', clean_sources
        print '>>>', clean_binaries

        if self.dry_run:
            print 'dry_run - not removing anything'
            return True

        os.system(clean_sources)

        if self.sysroot.is_mounted():
            os.system(clean_binaries)
        else:
            print 'Warning: sysroot is not mounted - cannot delete binaries'

        self.sysroot.umount()
