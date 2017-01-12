#!/usr/bin/env python
#
#  debianize-qt5.py
#
#  A rather rustic script to create debian packages from built QT5 libraries, using "dpkg-deb".
#
#  Syntax: qt5-debianize <sysroot directory> <qt5 install path>
#
#  If you run the script inside the chroot, simply pass "/" as the first argument.
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
Architecture: armhf
Depends: debconf (>= 0.5.00), {pkg_depends}
Priority: optional
Description: {pkg_description}

'''

# These are the X11 libraries on which QT5 depends on, provides XCB subsystem
extra_deps = 'libx11-xcb1, libxcb-icccm4, libxcb-xfixes0, libxcb-image0, libxcb-keysyms1, libxcomposite1, ' \
    'libxcb-randr0, libxcb-render-util0, libxrender1, libxext6, libxcb-glx0, libfontconfig1, libxkbcommon0, ' \
    'libinput5, libts-0.0-0, libjpeg62-turbo, libasound2, libproxy1, libicu52'

# These are the packages we are building
# For the moment we are collecting everyting in one single Debian pkg
packages=[

    # TODO: Split all the libraries into individul packages (core, network, gui, etc)
    # There are 36 libraries and 17 plugin folders on QT 5.5

    { 'fileset': [ 'imports',
                   'lib/lib*.so.*',
                   'lib/lib*.so',
                   'lib/fonts/*',
                   'plugins',
                   'qml'
                   ],

      'pkg_name': 'libqt5all',
      'pkg_version': 0,
      'pkg_depends': '{}, libraspberrypi0'.format(extra_deps),
      'pkg_description': 'All QT5 Libraries and basic tools' },

    { 'fileset': [ 'include', 'mkspecs', # FIXME: mkspecs has large number of devices we will never use
                   'lib/*.a', 'lib/*.la', 'lib/*.prl', 'lib/cmake', 'lib/pkgconfig', 'translations' ],
      'pkg_name': 'libqt5all-dev',
      'pkg_version': 0,
      'pkg_depends': 'libqt5all, libqt5all-native-tools, libraspberrypi-dev',
      'pkg_description': 'All QT5 Development files' }
]


def pack_qt5(root_directory, source_directory, qt5_version, dry_run=False):

    complete_source='{}/{}'.format(root_directory, source_directory)

    # Sanity check
    if not os.path.exists(complete_source):
        print 'error: path not found', complete_source
        sys.exit(1)

    for pkg in packages:

        pkg['pkg_version'] = qt5_version

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

        # Cleanup anything related to webengine
        if not dry_run:
            cmd='find ' + target_files_path + ' -iname \*webengine\* -exec rm -rfv {} \;'
            os.system(cmd)

        # create the Debian control file for "dpkg-deb" tool to know what to pack
        if not dry_run:
            debian_dir=os.path.join(versioned_pkg_name, 'DEBIAN')
            if not os.path.exists(debian_dir):
                os.makedirs(debian_dir)
            with open(os.path.join(debian_dir, 'control'), 'w') as control_file:
                control_file.writelines(control_skeleton.format(**pkg))

        # copy the shlibs file for the runtime package
        if not dry_run:
            if pkg['pkg_name'] == 'libqt5all':
                os.system('cp -v {} {}/shlibs'.format('shlibs.local-qt5', debian_dir))

        # finally call dpkg-deb and generate a debian package
        if not dry_run:
            rc=os.system('dpkg-deb --build {}'.format(versioned_pkg_name))
        else:
            rc=0

        if not rc:
            print 'Package {} created correctly'.format(versioned_pkg_name)
        else:
            print 'WARNING: Error creating package {}'.format(versioned_pkg_name)
