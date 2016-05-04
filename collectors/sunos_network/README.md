# Network Collector

Uses the `kstat` interface to get NIC statistics. The raw
`kstat` counter values are used: the collector itself *does not*
compute rates or deltas. This should be done by your graphing
software.

## Options

* **`zones`**: tells the collector which zones to get
  statistics for. By default it will only do zone `0`, which is the
  global. Zones are mapped by their ID, which you can see in the
  output of `zoneadm list`. You can use the magic value `__all__` to
  get output for all zones on the box. There's a minor overhead in
  collecting zone information as `zoneadm` has to be run at the
  start of every collection. By default the collector will get
  statistics for the global zone only.

* **`nic`**: is a string or list of NICs to watch. Default is
  `<interface>`.

* **`fields`**: is used to supply a filter list of fields
  which you are interested in.  A metric will only be published if
  its name is an element of that array. Lots of things in the `net`
  module don't make much sense in a telemetry context. (Link speed,
  duplex setting etc.)

  Default fields are
  * `obytes64`: bytes successfully received
  * `rbytes64`: bytes successfully transmitted
  * `collisions`: collisions during transmit
  * `brdcstrcv`: broadcast *packets* successfully received
  * `brdcstxmt`: broadcast *packets* successfully transmitted
  * `ierrors`: packets received which contained errors
  * `oerrors`: packets not transmitted because they contained errors
  * `multircv`: multicast *packets* successfully received
  * `multixmit`: multicast *packets* successfully transmitted

[The Illumos `gld(7d)` man page](https://illumos.org/man/7D/gld)
explains pretty much all of the fields. The above selection is
fairly abitrary, and you may find a better fit for your application.

## Statistics

On an eight-core i7 box with eight zones, collection of the default
fields for all zones takes ~57ms.

### Examples

Get input and output, in bytes, for every zone.

```
[[ SunOSNetworkCollector ]]
enabled = True
zones = __all__
fields = obytes64,rbytes64
```

## Metric Paths
```
network.<zone>.<interface>.brdcstrcv
network.<zone>.<interface>.brdcstxmt
network.<zone>.<interface>.collisions
network.<zone>.<interface>.dl_idrops
network.<zone>.<interface>.dl_odrops
network.<zone>.<interface>.ierrors
network.<zone>.<interface>.ifspeed
network.<zone>.<interface>.ipackets
network.<zone>.<interface>.ipackets64
network.<zone>.<interface>.link_duplex
network.<zone>.<interface>.link_state
network.<zone>.<interface>.multircv
network.<zone>.<interface>.multixmt
network.<zone>.<interface>.norcvbuf
network.<zone>.<interface>.noxmtbuf
network.<zone>.<interface>.obytes
network.<zone>.<interface>.obytes64
network.<zone>.<interface>.oerrors
network.<zone>.<interface>.opackets
network.<zone>.<interface>.opackets64
network.<zone>.<interface>.phys_state
network.<zone>.<interface>.rbytes
network.<zone>.<interface>.rbytes64
```

## Bugs and Caveats

I don't currently have access to a multi-homed box, so using NICs
other than `net0` is untested and possibly unsupported.

I'd like to have this work for etherstubs and vswitches. We'll see
how that goes once I get my hands on some hardware which supports
them.
