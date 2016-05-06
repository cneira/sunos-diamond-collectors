"""
A library of functions to support my SunOS collectors
"""

import subprocess, re
from os import path
import kstat

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
# Miscellany

def wanted(have, want):
    """
    A filtering method.
    have: is the thing we know we have. This usually comes from an
        iteratable, and is a string.
    want: could be a list. True if 'want' is a member. Could be a
        regex, or a list containing a regex: compare. Could be
        '__all__', in which case we want whatever we 'have'.
    """

    assert isinstance(have, basestring)

    if want == '__all__': return True

    if have in want: return True

    if isinstance(want, basestring):
        if re.match(want, have): return True
    else:
        for item in want:
            if re.match(item, have): return True

    return False

#-------------------------------------------------------------------------
# Conversion stuff

def bytify(size, use_thousands = False):
    sizes = ['b', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']

    multiplier = 1000 if use_thousands else 1024

    try:
        chunks = re.match("^([\d\.]+)(\w)$", size)
        exponent = sizes.index(chunks.group(2))
        return float(chunks.group(1)) * multiplier ** exponent
    except:
        return size

#-------------------------------------------------------------------------
# kstat stuff

"""
Rather than write a complex, comprehensive general kstat accessor,
I'm making up what I need as I need it. This will (already is) turn
into a hotch-potch of similar methods but I'll cope.
"""

def kstat_class(kclass):
    """
    fetch kstats for all instances and names of the given class.
    Discards anything that's not a 'long'. This might turn out not
    to be right in every case, but at the moment, it is.
    """

    assert isinstance(kclass, basestring)

    ko = kstat.Kstat()
    ret = {}

    for module, instance, name, ks_class, ks_type, ksp in ko._iterksp():
        if ks_class == kclass:
            ret[name] = {}
            astat =  ko[module, instance, name]
            for k, v in astat.items():
                if isinstance(v, long): ret[name][k] = v

    return ret

def kstat_name(kname):
    """
    fetch kstats for multiple named stat groups within a module,
    removing the crtime and snaptime.  For the NFS stuff.
    """

    assert isinstance(kname, basestring)

    ko = kstat.Kstat(kname)
    el = kname.split(':')

    if len(el) != 3:
        raise ValueError('kname is not three parts')

    try:
        instance = int(el[1])
    except:
        raise ValueError('instance is not an integer')

    try:
        raw = ko[el[0], instance, el[2]]
    except KeyError:
        return {}

    return {k: v for k, v in raw.iteritems()
            if k != 'crtime' and k != 'snaptime' and k != 'class'}

def kstat_module(module, name_ptn):
    """
    Return a dict of everything matching "name_ptn" in all names and
    classes underneath "module".

    This was written for the disk_error collector, where it fetches,
    for instance the 'Hard Error' value from every `cmdkerror` name
    space.

    The kstat name is lowercased and whitespace replaced with an
    underscore.
    """

    assert isinstance(module, basestring)
    assert isinstance(name_ptn, basestring)

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
    Returns a single kstat value. I'll probably need something much
    more generic soon, but for now this does the job.
    """

    assert isinstance(kname, basestring)

    el = kname.split(':')

    if len(el) != 4:
        raise ValueError('kstat name is not four parts')

    try:
        instance = int(el[1])
    except:
        raise ValueError('instance is not an integer')

    ko = kstat.Kstat()

    try:
        return ko.__getitem__([el[0], instance, el[2]])[el[3]]
    except:
        return False

