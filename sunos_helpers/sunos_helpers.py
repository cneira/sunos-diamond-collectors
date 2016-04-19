import subprocess
import kstat
import re
from os import path

def run_cmd(cmd_str):
    """
    Run a command and return the output. Multiline output is sent
    back as an array, single line as a string
    """

    cmd_chunks = cmd_str.split()

    if not path.exists(cmd_chunks[0]):
        raise NotImplementedError("'%s' not found" % cmd_chunks[0])

    proc = subprocess.Popen(cmd_chunks,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (out, err) = proc.communicate()

    if out:
        out = out.strip().split('\n')

        if len(out) > 1:
            return out
        else:
            return out[0]
    else:
        raise Exception('error: %s' %err)

def kstat_val(kname):
    """
    Returns a single kstat value. I'll probably need something much more
    generic soon, but for now this does the job.
    """

    kc = kname.split(':')
    ko = kstat.Kstat()
    return ko.__getitem__([kc[0], int(kc[1]), kc[2]])[kc[3]]

