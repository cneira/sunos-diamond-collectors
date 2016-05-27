#!/bin/ksh

# A wrapper to quickly start up Diamond with my SunOS collectors. Just a
# dirty stop-gap.

# I install this in different places on Solaris and SmartOS.

PATH=/bin

ME=$(readlink -f $0)
BASE=$(print $ME | sed 's|/share.*||')
CDIR=${ME%/*}

export PYTHONPATH=${BASE}/share/sunos-diamond-collectors

[[ $(uname -v) == "joyent"* ]] && CF=sample-config-smartos.conf \
                               || CF=sample-config-solaris11.conf

${BASE}/bin/diamond -f -l --skip-pidfile -c ${CDIR}/${CF}
