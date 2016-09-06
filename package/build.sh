#!/bin/ksh

# This script builds a big fat tarball of the collectors, plus
# everything they need to run -- including a Python runtime! It's a
# very quick, very dirty hack for me to push the stuff out to my own
# machines for testing.
#
# This script does not (currently) compile Python, mainly because I
# don't have a SmartOS box at the moment on which to compile things,
# and I can't be bothered to write the API calls that would be
# necessary to run a build on a JPC box. Maybe another night.
#
# So, it fetches a pre-built Python tarball from a known location and
# uses that. It doesn't do SPARC at the moment, because my SPARC
# machine is on its side in a shed. It will.
#
# The Diamond codebase is my own fork, which contains full Wavefront
# support. Hopefully this will one day be merged into the official
# distribution.
#
# This is all as rough and crude as hell. I'm fine with that.
#

PYTHON_DIR=/storage/software/python
which gtar >/dev/null && TAR=gtar || TAR=tar
which gsed >/dev/null && SED=gsed || SED=sed
BASE=${0%%/*}

# For various legacy reasons I have to unpack the Solaris and
# SmartOS tarballs in different locations

function make_tarball
{
	# $1 is the OS type, 'solaris' or 'smartos'

	print "packaging for $1"
    TMPDIR=$(mktemp -d)
	print "building in $TMPDIR"

	print "extracting Python: ${PYTHON_DIR}/python-diamond-${1}.tar.gz"
	$TAR -zxf ${PYTHON_DIR}/python-diamond-${1}.tar.gz -C $TMPDIR

    print "Cloning Wavefront Diamond fork to $TMPDIR"
    git clone https://github.com/snltd/Diamond.git $TMPDIR/Diamond
    cd ${TMPDIR}/Diamond
    git fetch
    git checkout feature/wavefront_handler
    ${TMPDIR}/diamond/bin/python setup.py install

    [[ $1 == "smartos" ]] && loc="/opt/local" || loc="/opt"

    for prog in $(grep -l $TMPDIR ${TMPDIR}/diamond/bin/*)
    do
        print "fixing interpreter in $prog"
        $SED -i "s|${TMPDIR}|${loc}|" $prog
    done
    cd -

    print "copying in the SMF stuff"
    cp -Rp ${BASE}/smf $TMPDIR/diamond/

    print "installing SunOS collectors from Github"
    COL_DIR=${TMPDIR}/diamond/share/sunos-diamond-collectors
	git clone https://github.com/snltd/sunos-diamond-collectors $COL_DIR
	git clone https://github.com/pyhedgehog/kstat ${COL_DIR}/kstat
    OUT=${PYTHON_DIR}/diamond-${1}.tar.gz

    print "creating artefact $OUT"
    $TAR zcf $OUT -C $TMPDIR diamond
    rm -fr $TMPDIR
}

if grep -q SmartOS /etc/release
then
	make_tarball smartos
elif grep -q Solaris /etc/release
then
	make_tarball solaris
else
	print -u2 "unknown/unsupported platform"
	exit 2
fi
