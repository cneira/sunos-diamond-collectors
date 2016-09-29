#!/bin/ksh

# A wrapper to start diamond in debug mode, using the config in this
# directory. Also fetches the kstat module if you don't have it.

if ! test -d modules/kstat
then
    git clone https://github.com/pyhedgehog/kstat.git
    rm -fr kstat/.git*
fi

export PYTHONPATH="$(dirname $(readlink -f $0))/modules"

if [[ -f /opt/diamond/bin/diamond ]]
then
    DIAMOND=/opt/diamond/bin/diamond
elif [[ -f /opt/local/diamond/bin/diamond ]]
then
    DIAMOND=/opt/local/diamond/bin/diamond
else
    print -u2 "ERROR: can't find a Python diamond install"
    exit 1
fi

$DIAMOND -f -l --skip-pidfile -c diamond-test.conf
