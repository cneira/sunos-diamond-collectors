"""
A library of functions to support my SunOS collectors
"""

import subprocess
import re
import sys
import kstat
import struct
import string
from os import path

# ------------------------------------------------------------------------
# Command execution stuff


def run_cmd(cmd_str, pfexec=False, as_arr=False):
    """
    Run a command and return the output. Multiline output is sent
    back as an array, single line as a string, unless you specify
    otherwise.

    :param cmd_str: The command to run, as a string. Only allows one
        command (so no pipes) and the command must be fully qualified.
        (string)
    :param pfexec: Set to True to run the command with `pfexec`. (bool)
    :param as_arr: If this is True, then output is always sent as
        an array. This is useful for things which count lines of
        output. (bool)
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

        if len(out) > 1 or as_arr is True:
            return out
        else:
            return out[0]
    else:
        raise Exception('error: %s' % err)


def zoneadm():
    """
    Get a list of visible zones. This needs to always be an array,
    even if there's only one.

    :returns: output of zoneadm command, one zone per line.
    """

    ret = run_cmd('/usr/sbin/zoneadm list -pc')

    if isinstance(ret, basestring):
        return [ret]
    else:
        return ret


# ------------------------------------------------------------------------
# Conversion stuff


def bytify(size, use_thousands=False):
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

    if size == '-':
        return 0

    try:
        chunks = re.match("^(-?[\d\.]+)(\w)$", size)
        exponent = sizes.index(chunks.group(2))
        return float(chunks.group(1)) * multiplier ** exponent
    except:
        try:
            return float(size)
        except:
            raise ValueError

# ------------------------------------------------------------------------
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

            if not value:
                raise

            ret[key] = value
        except:
            ret[key] = None

    if ret['instance']:
        ret['instance'] = int(ret['instance'])

    return ret


def get_kstat(descriptor, only_num=True, no_times=False, terse=False,
              ks_class=None, statlist=None, single_val=False):
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
    :param ks_class: Allows you to filter on kstat class. To retrieve
        stats for a given class across all modules, use ':::' as the
        descriptor. (bool)
    :param statlist: Returns only the kstats named in this list. If it
        is not a string, it is converted to a list to avoid substring
        matching. (string, list)
    :param single_val Returns the first value it finds for the given
        kstat. Use with care: be very specific.
    :returns: a dict of 'kstat_name: value' pairs. All keys are
        lower-cased, and whitespace is replaced with underscores. If
        there are no matches, you get an empty dict. (dict)
    :raises: ValueError if arguments are of the wrong type.
    """
    assert isinstance(descriptor, basestring)
    assert isinstance(only_num, bool)
    assert isinstance(no_times, bool)
    assert isinstance(terse, bool)

    if isinstance(statlist, basestring):
        statlist = [statlist]

    d = kstat_req_parse(descriptor)
    ret = {}

    if d['module']:
        ko = kstat.Kstat(d['module'])
    else:
        ko = kstat.Kstat()

    for mod, inst, name, kclass, ks_type, ksp in ko._iterksp():
        if d['instance'] is not None and inst != d['instance']:
            continue

        if d['name'] is not None and name != d['name']:
            continue

        if ks_class is not None and kclass != ks_class:
            continue

        astat = ko[mod, inst, name]

        for k, v in astat.items():
            if d['statistic'] is not None and k != d['statistic']:
                continue

            if statlist is not None and statlist != ['__all__'] and \
                    k not in statlist:
                        continue
            if k == 'snaptime' or k == 'crtime':
                if no_times:
                    continue
                v = long(v)
            if only_num:
                try:
                    float(v)
                except:
                    continue

            if single_val:
                return v

            k = k.lower().replace(' ', '_')

            if not terse:
                k = '%s:%d:%s:%s' % (mod, inst, name, k)
            ret[k] = v

    return ret

# ------------------------------------------------------------------------
# /proc stuff

proc_parser = {
    'usage': {
        'fmt':  '@iilLlLlLlLlLlLlLlLlLlLlLlLlLlL13L',
        'keys': ('pr_lwpid', 'pr_count', 'pr_tstamp', 'pr_tstamp_ns',
                 'pr_create', 'pr_create_ns', 'pr_term', 'pr_term_ns',
                 'pr_rtime', 'pr_rtime_ns', 'pr_utime', 'pr_utime_ns',
                 'pr_stime', 'pr_stime_ns', 'pr_ttime', 'pr_ttime_ns',
                 'pr_tftime', 'pr_tftime_ns', 'pr_dftime', 'pr_dftime_ns',
                 'pr_kftime', 'pr_kftime_ns', 'pr_ltime', 'pr_ltime_ns',
                 'pr_slptime', 'pr_slptime_ns', 'pr_wtime', 'pr_wtime_ns',
                 'pr_stoptime', 'pr_stoptime_ns', 'pr_minf', 'pr_majf',
                 'pr_nswap', 'pr_inblk', 'pr_oublk', 'pr_msnd', 'pr_mrcv',
                 'pr_sigs', 'pr_vctx', 'pr_ictx', 'pr_sysc', 'pr_ioch'),
        'size32': 172,
        'size64': 336,
        'ts_t': ('pr_tstamp', 'pr_create', 'pr_term', 'pr_rtime',
                 'pr_utime', 'pr_stime', 'pr_ttime', 'pr_tftime',
                 'pr_dftime', 'pr_kftime', 'pr_ltime', 'pr_slptime',
                 'pr_wtime', 'pr_stoptime')
    },
    'psinfo': {
        # we don't read all of this. The LWP stuff is complicated,
        # and not relevant

        'fmt':  '@3i' + # flag nlwp zomb (int)
                '8i' + # pid ppid pgid sid uid euid gid
                'L' + # pr_addr
                'LLl' + #pr_size pr_rssize pr_ttydev
                '2H' + # pr_pctcpu pr_pctmem
                'lL lL lL' + # pr_start pr_time pr_ctime
                '16s 80s' + # pr_fname pr_psargs
                'ii' + # pr_wstat pr_argc
                'LL' + # pr_argv prenvp
                's' + # pr_dmodel
                '3sii' + # lwpsinfo_t
                'iiiii',  # pr_taskid pr_projid
        'keys': ('pr_flag', 'pr_nlwp', 'pr_pid', 'pr_ppid', 'pr_pgid',
                 'pr_sid', 'pr_uid', 'pr_euid', 'pr_gid', 'pr_egid',
                 'pr_addr', 'pr_size', 'pr_rssize', 'pr_pad1', 'pr_ttydev',
                 'pr_pctcpu', 'pr_pctmem', 'pr_start', 'pr_start_ns', 'pr_time',
                 'pr_time_ns', 'pr_ctime', 'pr_ctime_ns', 'pr_fname',
                 'pr_psargs', 'pr_wstat', 'pr_argc', 'pr_argv', 'pr_envp',
                 'pr_dmodel', 'pr_pad2', 'pr_taskid', 'pr_projid', 'pr_nzomb',
                 'pr_poolid', 'pr_zoneid', 'pr_contract'),
        'size32': 232,
        'size64': 288,
        'ts_t': ('pr_start', 'pr_time', 'pr_ctime'),
    },
}

def proc_info(p_file, pid):
    """
    Parses a /proc file, according to rules in the proc_parse
    structure. These files are binary structures, defined in the
    proc(4) man page.

    :param p_file: the file in the process /proc directory you wish
        to parse. Rules for parsing it must be described in
        proc_parser.  (string)
    :param pid: the PID of the process you wish to inspect. (int)
    :raises: NotImplemented if the p_file is unknown. IOError if the
        file can't be read. Passes through any exception raised when
        assembling the return value.
    :returns: a dict of keys (from proc_parser) and their values.
        Values of timestruc_t type are turned into straight nanoseconds.
    """

    try:
        parser = proc_parser[p_file]
    except:
        raise NotImplementedError("don't know how to parse '%s'" % p_file)

    p_path = path.join('/proc', str(pid), p_file)

    if sys.getsizeof(int()) == 12:
        length = parser['size32']
    else:
        length = parse['size64']

    try:
        raw = file(p_path, 'rb').read(length)
    except:
        raise IOError('could not read %s' % p_path)

    ret = dict(zip(parser['keys'], struct.unpack(parser['fmt'], raw)))

    for k in parser['ts_t']:
        ret[k] = (ret[k] * 1e9) + ret['%s_ns' % k]

    return ret

def bpc_to_pc(pc):
    """
    Convert one of psinfo's weird "binary fraction" percentage
    values to an actual percentage value. Method is copied from
    prstat(1).
    :param pc: raw value from psinfo
    :returns: float
    """
    return float(pc) * 100 / 0x8000


# ------------------------------------------------------------------------
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

    if want == '__all__':
        return True

    if want == '__none__' or not want:
        return False

    if regex:
        if isinstance(want, basestring):
            if re.match(want, have):
                return True
        else:
            for item in want:
                if re.match(item, have):
                    return True

    else:
        if isinstance(want, basestring):
            return True if want == have else False

    if have in want:
        return True

    return False


def zone_map(zoneadm, passthru='__all__'):
    """
    Return a map of zone ID to zone name. Can't be cached because
    zones could be rebooted and get a different ID mid-flight. This
    would be a problem if you were running from the global.

    :param zoneadm: the output of a `zoneadm list -pc` command.
        (string)
    :param passthru: a list of zones you want: everything else will
        be discarded. If there's no passthru, you get everything.
        Non-running zones are ignored. (string or list)
    :raises: NotImplementedError if it can't parse the zoneadm arg.
    :return: map of { zone_id: zone name}. (dict)
    """

    ret = {}

    for z in zoneadm:
        chunks = z.split(':')

        if len(chunks) < 8:
            raise NotImplementedError(
              'cannot parse zoneadm output: %d fields in %s' %
              (len(chunks), zoneadm))

        if chunks[0] == '-':
            continue

        if passthru == '__all__' or chunks[1] in passthru:
            ret[chunks[0]] = chunks[1]

    """
    Here's a cheat: if we're in an NGZ, we don't actually care about
    the zone ID. In fact, kstat `link` instances *don't* match to
    zone ID in NGZs. So, we fudge the key.
    """

    if len(zoneadm) == 1 and ret.keys()[0] != 'global':
        ret = {'0': ret.values()[0]}

    return ret


def grep(pattern, arr):
    """
    Return a list of elements of 'raw' which match 'pattern'
    :param pattern: a regex-string which will be matched against
    each element
    :param arr: a list of strings to match against.
    :returns: a list of matches. The list can be empty
    """

    assert isinstance(pattern, basestring)
    assert isinstance(arr, list)

    ret = []

    for el in arr:
        if re.search(pattern, el):
            ret.append(el)

    return ret


def handle_value(value):
    """
    Some things are human-format numbers. bytify() can deal with
    those. We can also get ratios (as in dedup) and percentages.
    :param value: a thing to parse. (string)
    """

    if value[-1] == 'x':
        return float(value[0:-1])

    if value[-1] == '%':
        return float(value[0:-1])

    if value[0].isdigit():
        return bytify(value)

    raise ValueError


def to_metric(raw, separator='/'):
    """
    Take something with "bad" characters in, and return it as a safe
    metric path. For instance, removing slashes from ZFS dataset names.
    """

    return raw.translate(string.maketrans(separator, '.'))

def contract_map():
    """
    returns a map of contract ID => SMF FMRI
    """

    raw = run_cmd('/bin/svcs -vHo ctid,fmri')
    ret = {}

    for l in raw:
        ct, svc = l.split()
        if ct != '-':
            ret[ct] = svc

    return ret
