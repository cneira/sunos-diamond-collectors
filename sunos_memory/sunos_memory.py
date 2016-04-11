import diamond.collector
import subprocess
import kstat
from os import path

class SunOSMemoryCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSMemoryCollector, self).get_default_config()
        config.update({
            'path':   'memory',
            })
        return config

    def collect(self):
        if not path.exists('/bin/pagesize'):
            raise NotImplementedError("platform not supported")

        proc = subprocess.Popen(['/bin/pagesize'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        (pagesize, err) = proc.communicate()

        ko = kstat.Kstat('zfs')
        kpg = ko.__getitem__(['unix', 0, 'system_pages'])['pp_kernel']
        self.publish('kernel', int(pagesize) * int(kpg))
