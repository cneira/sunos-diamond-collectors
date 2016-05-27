"""
A library of functions to support my SunOS collectors
"""

import subprocess, re, kstat
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

def kstat_req_parse(descriptor):
    """
    return a dict of kstat parts
    """
    parts = descriptor.split(':', 4)

    ret = {}

    for key in ['module', 'instance', 'name', 'statistic']:
        try:
            value = parts.pop(0)
            if not value: raise
            ret[key] = value
        except:
            ret[key] = None

    if ret['instance']: ret['instance'] = int(ret['instance'])
    return ret

def get_kstat(descriptor, only_num=True, no_times=False):
    """
    A general-purpose kstat accessor.

    :param descriptor: A standard kstat name like 'cpu:0:vm:softlock'.
        Omitting a field equates to a wildcard, just like kstat(1m). The
        module (first field) *must* be supplied. Mandatory. (string)
    :param only_num: By default, only numeric values are returned, If
        you want things which are non-numeric, set this to False. (bool)
    :param no_times: By default, if a statistic name is not specified,
        the 'crtime' and 'snaptime' fields will be returned, as longs.
        Set this to True to omit them. (bool)
    :returns: a dict of 'kstat_name: value' pairs. All keys are
        lower-cased, and whitespace is replaced with underscores. If
        there are no matches, you get an empty dict. (dict)
    :raises: ValueError if arguments are of the wrong type.
    """
    assert isinstance(descriptor, basestring)
    assert isinstance(only_num, bool)
    assert isinstance(no_times, bool)

    d = kstat_req_parse(descriptor)
    ret ={}

    if not d['module']: raise ValueError

    ko = kstat.Kstat(d['module'])

    for mod, inst, name, kclass, ks_type, ksp in ko._iterksp():
        if d['instance'] != None and inst != d['instance']: continue
        if d['name'] != None and name != d['name']: continue
        astat = ko[mod, inst, name]

        for k, v in astat.items():
            if d['statistic'] != None and k != d['statistic']: continue
            if k == 'snaptime' or k == 'crtime':
                if no_times: continue
                v = long(v)
            if only_num:
                try:
                    float(v)
                except:
                    continue

            k = k.lower().replace(' ', '_')
            ret['%s:%d:%s:%s' % (mod, inst, name, k)] = v

    return ret
