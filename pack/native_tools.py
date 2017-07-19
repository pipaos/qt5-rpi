#!/usr/bin/env python
#
#  native_tools.py
#

import sys
import os
import shutil
import glob


# This is Debian control file in a skeleton reusable block
control_skeleton='''
Maintainer: Albert Casals <skarbat@gmail.com>
Section: others
Package: {pkg_name}
Version: {pkg_version}
Conflicts: libqt5all-dev (<= 5.7-1)
Architecture: armhf
Depends: debconf (>= 0.5.00), {pkg_depends}
Priority: optional
Description: {pkg_description}

'''

postinst_script='''
#!/bin/bash

case "$1" in
    configure)
       mkdir -p mkdir -p /opt/rpi-tools/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian-x64/bin/
       ln -sf /usr/bin/gcc      /opt/rpi-tools/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian-x64/bin/arm-linux-gnueabihf-gcc
       ln -sf /usr/bin/g++      /opt/rpi-tools/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian-x64/bin/arm-linux-gnueabihf-g++
       ln -sf /usr/bin/objcopy  /opt/rpi-tools/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian-x64/bin/arm-linux-gnueabihf-objcopy
       ln -sf /usr/bin/strip    /opt/rpi-tools/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian-x64/bin/arm-linux-gnueabihf-strip
       ;;
esac

#DEBHELPER#

exit 0
'''

postrm_script='''
#!/bin/bash

case "$1" in
    remove)
       rm -f /usr/bin/qmake
       rm -rf /opt/rpi-tools
       ;;
esac

#DEBHELPER#

exit 0
'''

# Allows forget about setting PATH on build environments
qmake_link ='''#!/bin/bash
PATH=$PATH:/usr/local/qt5/bin /usr/local/qt5/bin/qmake
'''


extra_deps = ''

# These are the packages we are building
# For the moment we are collecting everyting in one single Debian pkg
packages=[

    { 'fileset': '',
      'pkg_name': 'libqt5all-native-tools',
      'pkg_version': 0,
      'pkg_depends': 'libqt5all-dev (>= 5.9-0)',
      'pkg_description': 'QT5 Native compilation tools for the RaspberryPI' }
]


def pack_tools(root_directory, source_directory, qt5_version, tools_directory, dry_run=False):

    complete_source='{}/{}'.format(root_directory, source_directory)

    # Sanity check
    if not os.path.exists(complete_source):
        print 'error: path not found', complete_source
        sys.exit(1)

    for pkg in packages:

        pkg['pkg_version'] = qt5_version
        pkg['fileset'] = [ tools_directory ]

        # allocate a versioned directory name for the package
        versioned_pkg_name = 'pkgs/{}_{}'.format(pkg['pkg_name'], qt5_version)
        print 'Processing package {}...'.format(versioned_pkg_name)

        # extract the files from the root file system preparing them for packaging
        target_directory = '{}/{}'.format (versioned_pkg_name, source_directory)

        for files in pkg['fileset']:

            # Complete the pathname to the target directory
            last_path = os.path.dirname(files)
            target_files_path='{}/{}'.format(target_directory, last_path)

            print 'Extracting {} into {}...'.format(os.path.join(complete_source, files), target_files_path)
            if not os.path.exists(target_files_path) and not dry_run:
                os.makedirs(target_files_path)

            if not dry_run:
                os.system('cp -rvP {} {}'.format(os.path.join(complete_source, files), target_files_path))

        # create the Debian control file for "dpkg-deb" tool to know what to pack
        if not dry_run:
            debian_dir=os.path.join(versioned_pkg_name, 'DEBIAN')
            if not os.path.exists(debian_dir):
                os.makedirs(debian_dir)
            with open(os.path.join(debian_dir, 'control'), 'w') as control_file:
                control_file.writelines(control_skeleton.format(**pkg))

        # package postinst & postrm scripts - resolve qmake PATH on native builds
        if not dry_run:
            postinst_filename='{}/postinst'.format(debian_dir)
            postrm_filename='{}/postrm'.format(debian_dir)
            qmake_filename='{}/usr/bin/qmake'.format(os.path.join(versioned_pkg_name))
            with open(postinst_filename, 'w') as f:
                f.write(postinst_script)
                os.system('chmod ugo+rx {}'.format(postinst_filename))

            with open(postrm_filename, 'w') as f:
                f.write(postrm_script)
                os.system('chmod ugo+rx {}'.format(postrm_filename))

            os.makedirs(os.path.dirname(qmake_filename))
            with open(qmake_filename, 'w') as f:
                f.write(qmake_link)
                os.system('chmod ugo+rx {}'.format(qmake_filename))

        # finally call dpkg-deb and generate a debian package
        if not dry_run:
            rc=os.system('dpkg-deb --build {}'.format(versioned_pkg_name))
        else:
            rc=0

        if not rc:
            print 'Package {} created correctly'.format(versioned_pkg_name)
        else:
            print 'WARNING: Error creating package {}'.format(versioned_pkg_name)
