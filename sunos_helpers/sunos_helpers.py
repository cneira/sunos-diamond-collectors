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
    back as an array, single line as a string.

    :param cmd_str: The command to run, as a string. Only allows one
        command (so no pipes) and the command must be fully qualified.
        (string)
    :param pfexec: Set to True to run the command with `pfexec`. (bool)
    :raises: NotImplementedErrror if the command is not found or if
        `pfexec` is requested but not present. An exception detailing
        the error if the command exits nonzero.
    :returns: a string if the command outputs a single line, otherwise
        an array with each line of output as an element.
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

def wanted(have, want, regex=False):
    """
    A very simple filtering method to allow users to simply list the
    metrics they want, rather than having to deal with regexes and
    whitelists or blacklists.

    :param have: Is the thing we know we have. This usually comes from an
        iteratable. (string)
    :param want: Could be a list. True if 'want' is a member.  Could be
        '__all__', in which case we want whatever we 'have'. Could be
        '__none__', in which case we don't want anything. (list, string)
    :param regex: Normally we only return True on "plain text" matches.
        If you wish to match on patterns, set this to True. (bool)
    :returns: True if we have what we want, otherwise False. (bool)
    """

    assert isinstance(have, basestring)

    if want == '__all__': return True
    if want == '__none__' or not want: return False

    if regex:
        if isinstance(want, basestring):
            if re.match(want, have):
                return True
        else:
            for item in want:
                if re.match(item, have): return True

    else:
        if isinstance(want, basestring):
            return True if want == have else False

    if have in want: return True

    return False

#-------------------------------------------------------------------------
# Conversion stuff

def bytify(size, use_thousands = False):
    """
    Feed it a number with an ISO suffix and it will give you back the
    bytes in that number.

    :param size: A size such as '5G' or '0.5P'. (string)
    :param use_thousands: by default we assume 1024 bytes in a kilobyte
        etc. Set this to True to assumer 1000. (bool)
    :raises: ValueError if we don't know what to do with the input.
    :return: the number of bytes. (float)
    """

    sizes = ['b', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']

    multiplier = 1000 if use_thousands else 1024

    try:
        chunks = re.match("^(-?[\d\.]+)(\w)$", size)
        exponent = sizes.index(chunks.group(2))
        return float(chunks.group(1)) * multiplier ** exponent
    except:
        try:
            return float(size)
        except:
            raise ValueError

#-------------------------------------------------------------------------
# kstat stuff

def kstat_req_parse(descriptor):
    """
    Return a dict of kstat parts.

    :param descriptor: The description of a kstat in one to four
        colon-separated parts. (string)
    :returns: a dict with keys 'module', 'instance', 'name', and
        'statistic'. Values are the parts of the kstat name passed in,
        or None.
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

def get_kstat(descriptor, only_num=True, no_times=False, terse=False):
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
    :param terse: The keys of the returned dict will normally contain
        the full, four-part kstat name. If you set this parameter to
        True, only the statistic name will be used in the key. This
        option is potentially risky, as multiple instances will
        overwrite one another. Useful, to to be used with caution.
        (bool)
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
            if not terse: k = '%s:%d:%s:%s' % (mod, inst, name, k)
            ret[k] = v

    return ret
