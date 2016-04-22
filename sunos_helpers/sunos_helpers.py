"""
A library of functions to support my SunOS collectors
"""

import subprocess
import kstat
import re
from os import path

#-------------------------------------------------------------------------
# Command execution stuff

def run_cmd(cmd_str, pfexec=False):
    """
    Run a command and return the output. Multiline output is sent
    back as an array, single line as a string. Lets you elevate
    privs with pfexec if you wish it.
    """

    cmd_chunks = cmd_str.split()

    if not path.exists(cmd_chunks[0]):
        raise NotImplementedError("'%s' not found" % cmd_chunks[0])

    if pfexec:
        if not path.exists('/bin/pfexec'):
            raise NotImplementedError('pfexec not found')

        cmd_chunks.insert(0, '/bin/pfexec')

    proc = subprocess.Popen(cmd_chunks,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (out, err) = proc.communicate()

    if proc.returncode == 0:
        out = out.strip().split('\n')

        if len(out) > 1:
            return out
        else:
            return out[0]
    else:
        raise Exception('error: %s' %err)

#-------------------------------------------------------------------------
# Conversion stuff

def to_bytes(size):

    sizes = ['b', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']

    try:
        chunks = re.match("^([\d\.]+)(\w)$", size)
        exponent = sizes.index(chunks.group(2))
        return float(chunks.group(1)) * 1024 ** exponent
    except:
        return size

#-------------------------------------------------------------------------
# kstat stuff

def kstat_module(module, name_ptn):
    """
    Return a dict of everything matching "name_ptn" in the "module".
    This was written for the disk_error collector, but will
    hopefully be useful elsewhere.

    The kstat name is lowercased and whitespace replaced with an
    underscore.
    """

    ko = kstat.Kstat(module)
    items = {}

    for x in ko._iterksp():
        kmodule, kinstance, kname, kclass, ktype, ksp = x
        astat =  ko[kmodule, kinstance, kname]
        for k, v in astat.items():
            if re.match(name_ptn, k):
                items['%s.%s' % (kname, k.lower().replace(' ', '_'))] = v

    return items


def kstat_val(kname):
    """
    Returns a single kstat value. I'll probably need something much more
    generic soon, but for now this does the job.
    """

    kc = kname.split(':')
    ko = kstat.Kstat()
    return ko.__getitem__([kc[0], int(kc[1]), kc[2]])[kc[3]]

