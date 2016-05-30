# Zones Collector

Uses the `zoneadm` command to produce metrics describing the number of
zones in all possible states.

## Options

* **`states`** : You can use Diamond's blacklist/whitelist options to
  filter metrics or change this parameter to be a list of only the zone
  states you are interested in.

### Examples

Count the number of `running` zones.

```
[[ ZonesCollector ]]
enabled = True
states = running
```

## Bugs and Caveats

This collector doesn't make a whole heap of sense in a non-global zone.

## Metric Paths

```
zone.count.configured
zone.count.down
zone.count.incomplete
zone.count.installed
zone.count.ready
zone.count.running
zone.count.shutting_down
```
