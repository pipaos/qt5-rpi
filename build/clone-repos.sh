#!/bin/bash
#
#  Clone the QT5 sources.
#
#  Execute this script on the Intel host, from a directory inside the chroot.
#
#   clone-repos.sh <qt5 branch> (as of this writing, "5.5")
#

qt5_branch=$1
if [ "$qt5_branch" == "" ]; then
    echo "Syntax: native-clone.sh <QT5 branch>"
    exit 1
fi

# Get the QT5 sources
qt5_src_dir="qt5"
if [ ! -d "$qt5_src_dir" ]; then
    echo ">>> cloning QT5 sources"
    git clone --branch=$qt5_branch git://code.qt.io/qt/qt5.git
    if [ "$?" != "0" ]; then
        echo "Error cloning QT5 sources"
        exit 1
    fi
fi

# init-repository
repo_initialized="./init-repo-done"
if [ ! -f "$repo_initialized" ]; then
    echo ">>> initializing QT5 repos"
    pushd $qt5_src_dir
    perl init-repository
    if [ "$?" != "0" ]; then
        echo "init-repository failed"
        popd
        exit 1
    else
        touch $repo_initialized
    fi
    popd
fi
