#!/usr/bin/env python
#
#  debianize-webengine.py
#
#  A rather rustic script to package QT5 Webengine into a Debian package
#
#  Syntax: webengine-debianize <sysroot directory> <qt5 install path>
#
#  If you run the script inside the chroot, simply pass "/" as the first argument.
#

import sys
import os
import shutil
import glob

# This is the version of the Debian package
qt5_version = '5.7-1'

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

# Webengine extra core dependencies
extra_deps=''

packages=[

    # QtWebEngine Runtime package
    { 'fileset': [ 'translations/qtwebengine_locales/*',
                   'resources/qtwebengine_resources*pak',
                   'resources/qtwebengine_devtools_resources.pak',
                   'resources/icudtl.dat',
                   'lib/libQt5WebEngine*',
                   'qml/QtWebEngine/*',
                   'libexec/QtWebEngineProcess'
               ],
  
      'pkg_name': 'libqt5webengine',
      'pkg_version': qt5_version,
      'pkg_depends': 'libqt5all{}'.format(extra_deps),
      'pkg_description': 'QT5 WebEngine Libraries and basic tools'
  },

    # QtWebEngine Developer's package
    { 'fileset': [ 'include/QtWebEngineWidgets/*',
                   'include/QtWebEngine/*',
                   'include/QtWebEngineCore/*',
                   'mkspecs/modules/qt_lib_webengine*',
                   'lib/cmake/Qt5WebEngine*',
                   'lib/pkgconfig/Qt5WebEngine*'
               ],
  
      'pkg_name': 'libqt5webengine-dev',
      'pkg_version': qt5_version,
      'pkg_depends': 'libqt5webengine',
      'pkg_description': 'QT5 WebEngine Libraries and basic tools'
  }
    
]


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print 'Syntax: webengine-debianize <sysroot directory> <qt directory>'
        print '        sysroot : pathname of the image mount point'
        print '        qt directory : pathname inside the root (i.e. /usr/local/qt-v5.4.1)'
        sys.exit(1)
    else:
        root_directory=sys.argv[1]
        source_directory=sys.argv[2]
        complete_source='{}/{}'.format(root_directory, source_directory)

    # Sanity check
    if not os.path.exists(complete_source):
        print 'error: path not found', complete_source
        sys.exit(1)

    for pkg in packages:

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
            if not os.path.exists(target_files_path):
                os.makedirs(target_files_path)

            os.system('cp -rvP {} {}'.format(os.path.join(complete_source, files), target_files_path))

        # create the Debian control file for "dpkg-deb" tool to know what to pack
        debian_dir=os.path.join(versioned_pkg_name, 'DEBIAN')
        if not os.path.exists(debian_dir):
            os.makedirs(debian_dir)
        with open(os.path.join(debian_dir, 'control'), 'w') as control_file:
            control_file.writelines(control_skeleton.format(**pkg))

        # copy the shlibs file for the runtime package
        if pkg['pkg_name'] == 'libqt5webengine':
            os.system('cp -v {} {}/shlibs'.format('shlibs.local-webengine', debian_dir))

        # finally call dpkg-deb and generate a debian package
        rc=os.system('dpkg-deb --build {}'.format(versioned_pkg_name))
        if not rc:
            print 'Package {} created correctly'.format(versioned_pkg_name)
        else:
            print 'WARNING: Error creating package {}'.format(versioned_pkg_name)
