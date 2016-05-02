# coding=utf8

"""
Zone Status Collector

#### Dependencies

 * /usr/sbin/zoneadm

"""

import diamond.collector
import sunos_helpers

class ZonesCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(ZonesCollector, self).get_default_config()
        config.update({
            'path':   'zone',
            'states': ['configured', 'down', 'incomplete',
                       'installed', 'ready', 'running', 'shutting_down'
                      ],
            })
        return config

    def zoneadm(self):
        return sunos_helpers.run_cmd('/usr/sbin/zoneadm list -pc')

    def collect(self):
        zones = [z.split(':')[2] for z in self.zoneadm()]

        for state in self.config['states']:
            self.publish('count.' + state, zones.count(state))
