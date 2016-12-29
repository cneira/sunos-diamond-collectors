# coding=utf8

"""
SMF Service Collector

Uses the system 'svcs' command to count how many services are in
each possible state. This is intended for simple alerting off failed
services. I can't see why you'd ever want to know how many states
are in 'legacy_run' or 'disabled', but the option is there if you
want it. Indeed, by default all possible service states are
reported, but the user can choose their own with the 'states'
option.

Illomos' 'svcs' is zone-aware. From the global, you can query the
service states in all zones. The only way to do this on Solaris is
with some kind of 'zlogin' approach which, for now, I have decided
not to take.

When Diamond runs in the global zone, NGZ statistics appear under
'smf.svcs.ngz.<zone_name>'.

#### Dependencies

 * /bin/svcs


#### Example

Only send counts of services which are uninitialized, degraded,
offline, or in maintenance state.

    states = uninitialized,degraded,offline,maintenance

"""

import diamond.collector
import sunos_helpers as sh


class SmfSvcCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SmfSvcCollector, self).get_default_config()
        config.update({
            'zones':  '__all__',
            'path':   'smf.svcs',
            'states': ['online', 'offline', 'uninitialized',
                       'degraded', 'maintenance', 'legacy_run',
                       'disabled']
            })
        return config

    def process_zone(self, data):
        # return a hash of counts for each service state

        ret = {}

        for state in self.config['states']:
            ret[state] = data.count(state)

        return ret

    def process_data(self, data):
        ret = {}

        if len(data[0].split()) == 2:
            for z in set([l.split()[0] for l in data]):
                zd = [l.split()[1] for l in data if l.split()[0] == z]
                ret[z] = self.process_zone(zd)
        elif len(data[0].split()) == 1:
            ret['__local__'] = self.process_zone(data)
        else:
            raise 'cannot parse svcs output'

        return ret

    def svcs(self):
        try:
            ret = sh.run_cmd('/bin/svcs -ZaHo zone,state')
        except:
            ret = sh.run_cmd('/bin/svcs -aHo state')

        return ret

    def collect(self):
        svcs = self.process_data(self.svcs())

        for zone, data in svcs.items():
            if not sh.wanted(zone, self.config['zones']):
                continue

            if zone == '__local__' or zone == 'global':
                prefix = ''
            else:
                prefix = 'ngz.%s.' % zone

            for state, count in data.items():
                if sh.wanted(state, self.config['states']):
                    self.publish(prefix + state, count)
