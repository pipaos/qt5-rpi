#!/usr/bin/env python
#
#  host-bootstrap.sh
#
#  Prepares the host to build QT5 for the RaspberryPI.
#

import os
import sys
import platform

def supported_platform():
    arch, elf = platform.architecture()
    if not arch=='64bit':
        print 'Supported platform is 64bit only'
        return False

    return True

def sudo_working():
    command='sudo -k -n whoami'
    am_i_root=os.popen(command).read().strip()
    if am_i_root != 'root':
        print 'please, enable sudo password-less option'
        return False
    return True

def cross_compiler():
    '''assuming 64 bit platform'''
    env_found=False
    opt_path='/opt/rpi-tools'
    gcc_path='{}/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian-x64/bin'.format(opt_path)
    gcc='arm-linux-gnueabihf-gcc'
    gplusplus='arm-linux-gnueabihf-g++'

    download_command='sudo git clone https://github.com/raspberrypi/tools.git /opt/rpi-tools'    
    if not os.path.isdir(opt_path):
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

    rc=os.system('{}/{} --version'.format(gcc_path, gcc))
    if rc:
        print 'C cross compiler does not seem to run'
        return False

    rc=os.system('{}/{} --version'.format(gcc_path, gplusplus))
    if rc:
        print 'C++ cross compiler does not seem to run'
        return False

    return True

def xsysroot_installed(profile='qt5build'):
    url='https://raw.githubusercontent.com/skarbat/xsysroot/master/xsysroot'
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
    if os.system('xsysroot -p {} -s'.format(profile)):
        print 'WARNING: Please install xsysroot.conf on your homedir or /etc'
        return False
    
    return True

def build_dependencies():
    packages='build-essential pkg-config gperf bison ruby'
    rc=os.system('sudo apt-get install -y --no-install-recommends {}'.format(packages))
    return rc==0


if __name__ == '__main__':

    checks = [ supported_platform, sudo_working, cross_compiler, xsysroot_installed, build_dependencies ]

    for validate in checks:
        print 'validating {}...'.format(validate.__name__)
        if not validate():
            print '> check failed!'
            sys.exit(1)

    print 'Good! Host setup seems to be fine'
    sys.exit(0)
