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

PYTHON_VER=2.7.14
BUILD_DIR=/build
CC=gcc
CFLAGS="-O2"

# For various legacy reasons I have to unpack the Solaris and
# SmartOS tarballs in different locations

die() {
    print -u2 $1
    exit ${2:-1}
}

msg() {
    print $*
}

compile_python()
{
    if [[ ! -f ${BUILD_DIR}/Python-${PYTHON_VER}.tgz ]]
    then
        msg "fetching Python ${PYTHON_VER} source"
        wget --no-check-certificate -q -P $BUILD_DIR \
            https://www.python.org/ftp/python/${PYTHON_VER}/Python-${PYTHON_VER}.tgz
    fi

    msg "clearing ${BUILD_DIR}/Python-${PYTHON_VER}"
    rm -fr ${BUILD_DIR}/Python-${PYTHON_VER}

    msg "unpacking archive into $BUILD_DIR"
    $TAR zxf ${BUILD_DIR}/Python-${PYTHON_VER}.tgz -C $BUILD_DIR

    cd ${BUILD_DIR}/Python-${PYTHON_VER}

	# I simply cannot find a way to make `Setup.py` find the zlib
	# and openssl headers on SmartOS. Hence this:

	if [[ -n $IS_SMARTOS ]]
	then
		msg "altering ${BUILD_DIR}/Python-${PYTHON_VER}/setup.py"
		$SED -i 's|usr/local|opt/local|g' \
			${BUILD_DIR}/Python-${PYTHON_VER}/setup.py
	fi

    msg "configuring with prefix '$TMPDIR/diamond'"

    CC=$CC CFLAGS=$CFLAGS LDFLAGS=-m64 \
		./configure --prefix=${TMPDIR}/diamond \
					--build=i386-pc-solaris2.11 \
					--host=i386-pc-solaris2.11 \
	                --enable-optimizations \
					--enable-shared=no >/dev/null 2>&1

    msg "compiling Python"
    gmake -j4 >/dev/null 2>&1 || die 'could not compile Python'

    msg "installing Python into ${TMPDIR}/diamond"
    gmake install
    cd -
}

install_python_extras()
{
    if [[ ! -f ${TMPDIR}/diamond/bin/pip ]]
    then
        wget -q -P $BUILD_DIR https://bootstrap.pypa.io/get-pip.py
        ${TMPDIR}/diamond/bin/python ${BUILD_DIR}/get-pip.py
    fi

    ${TMPDIR}/diamond/bin/pip install configobj
}

setup_base_python()
{
    # if we're given a path to a pre-built Python tarball, unpack
    # that. If not, fetch Python and compile it.

    if [[ -n $1 ]]
    then
        test -f $1 || die "no Python archive at $1"
        msg "extracting precompiled Python $1"
	    $TAR zxf $1 -C $TMPDIR
    else
        msg "Intending to compile Python from source"
        compile_python
    fi
}

install_fork()
{
    print "Cloning Wavefront Diamond fork to $TMPDIR"
    rm -fr ${TMPDIR}/Diamond
    git clone https://github.com/snltd/Diamond.git ${TMPDIR}/Diamond
    cd ${TMPDIR}/Diamond
    git fetch
    git checkout feature/wavefront_handler
    $SED -i "s|/etc/diamond|${TMPDIR}/diamond/etc|" setup.py
    ${TMPDIR}/diamond/bin/python setup.py install

	ggrep -Il $TMPDIR ${TMPDIR}/diamond/bin/* | while read prog
    do
        print "fixing interpreter in $prog"
        $SED -i "s|${TMPDIR}|${LOC}|" $prog
    done
    cd -
}

install_smf()
{
    mkdir -p ${TMPDIR}/diamond/lib/svc

    if [[ $IS_SMARTOS ]]
    then
        print "munging the SMF stuff for SmartOS"
        mkdir -p ${TMPDIR}/diamond/lib/svc/manifest \
                 ${TMPDIR}/diamond/lib/svc/method

        sed "s|/opt/diamond|/opt/local/diamond|" \
            ${BASE}/smf/method/diamond \
            >${TMPDIR}/diamond/lib/svc/method/diamond

        sed "s|/opt/diamond|/opt/local/diamond|" \
            ${BASE}/smf/manifest/diamond.xml \
            >${TMPDIR}/diamond/lib/svc/manifest/diamond.xml

        chmod 755 ${TMPDIR}/diamond/lib/svc/method/diamond
    else
        print "copying in the SMF stuff"
        cp -Rp ${BASE}/smf/* $TMPDIR/diamond/lib/svc
    fi
}

install_sunos_collectors()
{
    print "installing SunOS collectors from Github"
    COL_DIR=${TMPDIR}/diamond/share/sunos-diamond-collectors

	git clone https://github.com/snltd/sunos-diamond-collectors \
		$COL_DIR >/dev/null
	git clone https://github.com/pyhedgehog/kstat \
        ${COL_DIR}/modules/kstat >/dev/null
}

create_pkgin()
{
	P_DIR=${TMPDIR}/pkgin
	PKG_NAME=sdef-diamond-$(date "+%Y%m%d%H%M").tgz
	mkdir -p $P_DIR

	find ${TMPDIR}/diamond ! -type d \
		| sed "s|${TMPDIR}/||" >${P_DIR}/pkglist

	/opt/local/sbin/pkg_info -X pkg_install \
		| egrep '^(MACHINE_ARCH|OPSYS|OS_VERSION|PKGTOOLS_VERSION)' \
		>${P_DIR}/build-info

	print "Diamond metric collector for SmartOS. Python $PY_VER" \
		>${P_DIR}/comment

	print "Diamond metric collector for SmartOS" >${P_DIR}/description

    /opt/local/sbin/pkg_create \
		-v \
        -B ${P_DIR}/build-info \
        -d ${P_DIR}/description \
        -c ${P_DIR}/comment \
        -f ${P_DIR}/pkglist \
        -I $LOC \
        -p ${TMPDIR} \
        ${HOME}/${PKG_NAME}
}

create_artefact()
{
	OUT=${PYTHON_DIR}/diamond-${1}-$(date "+%Y%m%d%H%M").tar.gz

	if [[ $IS_SMARTOS ]]
	then
		create_pkgin
	else
		msg "creating artefact $OUT"
		$TAR zcf $OUT -C $TMPDIR diamond
	fi

    rm -fr $TMPDIR
}

build()
{
    # $1 is the platform
    # $2 is the path to a pre-built Python archive

	print "packaging for $1"
    setup_base_python $2
    install_python_extras
    install_fork
    install_sunos_collectors
    install_smf
    create_artefact $1
}

TMPDIR=$(mktemp -d -p /var/tmp)

print "building in $TMPDIR"

if grep -q SmartOS /etc/release
then
	IS_SMARTOS=true
    LOC=/opt/local
	CFLAGS="-m32"
	LDFLAGS="-m32"
	build smartos $1
elif grep -q Solaris /etc/release
then
    LOC=/opt
    CC=cc
    CFLAGS="-xarch=native -m64"
	build solaris $1
else
	print -u2 "unknown/unsupported platform"
	exit 2
fi
