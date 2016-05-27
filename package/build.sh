#!/bin/ksh

# This script builds a big fat tarball of the collectors, plus
# everything they need to run -- including a Python runtime!
#
# It does not (currently) compile Python, mainly because I don't have a
# SmartOS box at the moment on which to compile things, and I can't be
# bothered to write the API calls that would be necessary to run a build
# on a JPC box. Maybe another night.
#
# So, it fetches a pre-built Python tarball from a known location and
# uses that.
#
# This is all as rough and crude as hell. I'm fine with that.
#

PYTHON_DIR=/storage/software/python
which gtar >/dev/null && TAR=gtar || TAR=tar
#TMPDIR=/tmp/diamond_build
TMPDIR=/opt

# For various legacy reasons I have to unpack the Solaris and SmartOS
# tarballs in different locations

function make_tarball
{
	# $1 is the OS type, 'solaris' or 'smartos'

	mkdir -p $TMPDIR
	#print "  flushing build directory"
	rm -fr ${TMPDIR}/diamond
	#print "  creating build directory"
	print "  extracting base archive"
	$TAR -zxf ${PYTHON_DIR}/python-diamond-${1}.tar.gz -C $TMPDIR

	git clone https://github.com/snltd/sunos-diamond-collectors \
		${TMPDIR}/diamond/share/sunos-diamond-collectors

	git clone https://github.com/pyhedgehog/kstat \
		${TMPDIR}/diamond/share/kstat
}

for platform in solaris11 #smartos
do
	print "doing the do for $platform"
	make_tarball $platform
done
