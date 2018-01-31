import diamond.collector
import sunos_helpers as sh


class SunOSSmbServerCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSSmbServerCollector, self).get_default_config()
        config.update({'fields':   '__all__',
                       'path':     'smb.server',
                       })
        return config

    def kstats(self):
        return sh.get_kstat('smbsrv:0:smb2_commands', terse=True,
                            no_times=True)

    def collect(self):
        for k, v in self.kstats().items():
            self.publish(k, v)
