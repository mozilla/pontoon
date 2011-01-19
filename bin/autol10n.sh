#!/bin/bash

# Automatically pull L10n dirs from SVN, compile, then push to git.
# Runs on all project dirs named *-autol10n.

# Settings
GIT=`/usr/bin/which git`
FIND=`/usr/bin/which find`
DEVDIR=$HOME/dev

# Update everything
for dir in `$FIND "$DEVDIR" -maxdepth 1 -name '*-autol10n'`; do
cd $dir
    $GIT pull -q origin master
    cd locale
    $GIT svn rebase

    # Compile .mo, commit if changed
    ./compile-mo.sh .
    $FIND . -name '*.mo' -exec $GIT add {} \;
    $GIT status
    if [ $? -eq 0 ]; then
        $GIT commit -m 'compiled .mo files (automatic commit)'
    fi

    # Push to SVN and git
    $GIT svn dcommit && $GIT push -q origin master

    cd ..

    $GIT add locale
    $GIT status locale
    if [ $? -eq 0 ]; then
        $GIT commit -m 'L10n update (automatic commit)'
        $GIT push -q origin master
    fi
done
