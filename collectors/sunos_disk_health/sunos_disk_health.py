import diamond.collector, re
import sunos_helpers as sh

class SunOSDiskHealthCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSDiskHealthCollector, self).get_default_config()
        config.update({
            'modules': ['cmdkerror', 'sderr'],
            'fields':  ['hard_errors', 'soft_errors' 'transport_errors',
                        'device_not_ready', 'illegal_request',
                        'predictive_failure_analysis'],
            'path':    'disk.error',
            'sn_tag':   True,
            'sn_fields': ['Model', 'Serial No', 'Vendor', 'Product'],
            })
        return config

    def disk_tags(self):
        """
        Wavefront gives us the ability to tag points. If the user
        wishes, we will tag each point with the model name and serial
        number of the disk, producing more meaningful alerts
        """

        ret = {}

        for k, v in sh.get_kstat(':::', ks_class='device_error',
                only_num=False, statlist=self.config['sn_fields']).items():
            dev, stat = list(re.split('[:,]', k)[i] for  i in (2,-1))
            if dev not in ret: ret[dev] = {}
            ret[dev][stat] = v.strip()

        return ret

    def kstats(self, module):
        return sh.get_kstat(module, no_times=True, )

    def collect(self):
        if self.config['sn_tag']:
            point_tags = self.disk_tags()

        for mod in self.config['modules']:
            for k, v in self.kstats(mod).items():
                dev, stat = list(re.split('[:,]', k)[i] for  i in (2,-1))
                if sh.wanted(stat, self.config['fields']):
                    if self.config['sn_tag'] and dev in point_tags.keys():
                        self.publish('%s.%s' % (dev, stat), v,
                                point_tags=point_tags[dev])
                    else:
                        self.publish('%s.%s' % (dev, stat), v)
