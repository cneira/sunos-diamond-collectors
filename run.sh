#!/bin/ksh

# A wrapper to start diamond in debug mode, using the config in this
# directory. Also fetches the kstat module if you don't have it.

if ! test -d kstat
then
    git clone https://github.com/pyhedgehog/kstat.git
fi

/opt/diamond/bin/diamond -f -l --skip-pidfile -c diamond-test.conf
