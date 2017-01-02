#!/usr/bin/env python
#
#  host-bootstrap.sh
#
#  Prepares the host to build QT5 for the RaspberryPI.
#

import os
import sys
import platform

from builder import Builder

class BuilderPrepare(Builder):

    def supported_platform(self):
        arch, elf = platform.architecture()
        if not arch=='64bit':
            print 'Supported host platform is 64bit only'
            return False
    
        return True

    def sudo_working(self):
        command='sudo -k -n whoami'
        am_i_root=os.popen(command).read().strip()
        if am_i_root != 'root':
            print 'please, enable sudo NOPASSWD option'
            return False
        return True

    def cross_compiler(self):
        '''assuming 64 bit platform'''
        env_found=False
        gcc_path='{}/{}'.format(self.config['rpi_tools'], self.config['xgcc_path64'])

        download_command='sudo git clone {}'.format(self.config['rpi_tools_url'])
        if not os.path.isdir(self.config['rpi_tools']):
            print 'installing a cross compiler'
            if os.system(download_command):
                return False

            for p in os.environ['PATH'].split(':'):
                if p == gcc_path:
                    env_found=True

            if not env_found:
                print 'Please, add this entry to your PATH:'
                print gcc_path
            return False

        rc=os.system('{}/{}gcc --version'.format(gcc_path, self.config['xgcc_suffix']))
        if rc:
            print 'C cross compiler does not seem to run'
            return False

        rc=os.system('{}/{}g++ --version'.format(gcc_path, self.config['xgcc_suffix']))
        if rc:
            print 'C++ cross compiler does not seem to run'
            return False
    
        return True

    def xsysroot_installed(self):
        url=self.config['xsysroot_url']
        installed='/usr/local/bin/xsysroot'
        install_cmd='sudo curl -L --output {} "{}" && sudo chmod +x {}'.format(installed, url, installed)
    
        try:
            import xsysroot
        except:
            if not os.system(install_cmd):
                print 'Error installing xsysroot'
                return False

            if os.system('sudo xsysroot -U'):
                print 'Error upgrading xsysroot'
                return False
        
        try:
            import xsysroot
        except:
            print 'Could not install xsysroot'
            return False

        print 'xsysroot installed version', xsysroot.__version__
        if os.system('xsysroot -p {} -s'.format(self.config['xsysroot_profile'])):
            print 'WARNING: Please install xsysroot.conf on your homedir or /etc'
            return False
    
        return True

    def install_dependencies(self):
        rc=os.system('sudo apt-get install -y --no-install-recommends {}'.format(
            self.config['host_dependencies']))
        return rc==0


if __name__ == '__main__':

    prepare=BuilderPrepare('buildqt5.json')
    checks = [ prepare.supported_platform,
               prepare.sudo_working,
               prepare.cross_compiler,
               prepare.xsysroot_installed,
               prepare.install_dependencies ]

    for validate in checks:
        print 'validating {}...'.format(validate.__name__)
        if not validate():
            print '> check failed!'
            sys.exit(1)

    print 'Good! Host setup seems to be fine'
    sys.exit(0)
