# SmartOS Zone Collector

This collector tries to be a one-stop-shop for all the useful CPU and
memory measurables inside a SmartOS zone.

The view from an NGZ is very different from the global, with many metrics
reflective of the physical host, or unavailable. This means many of the
collectors in this package are not particularly useful. However, you
would likely want to run the `SunOSMemoryCollector` and possibly
`SMFSvcCollector` along with this one.

Joyent have made sufficient changes to the `kstat` view from an NGZ that
you probably won't get an awful lot of mileage using this in, say, a
Solaris 11 zone.

## Options

## Statistics

### Examples

```
[[ SmartOSZoneCollector ]]
enabled = True
```

## Metric Paths

Max Bruning has written [an excellent description of SmartOS memory
capping](https://www.joyent.com/blog/memory-capping-on-smartos) which
explains some of the following metrics, and Brendan Gregg refers to some
of them in [a piece on the USE performance
methodology](http://www.brendangregg.com/USEmethod/use-smartos.html).

[The `zonecfg(1m)` man page](https://illumos.org/man/1m/zonecfg)
explains some part of CPU capping, but [the `cpucaps.c` source code
contains an excellent
description](https://github.com/joyent/illumos-joyent/blob/master/usr/src/uts/common/disp/cpucaps.c#L40-L193)
of how it really works.

I've made short annotations of each metric, but I'd advise you to read
the above links, particularly [the part on
bursting](https://github.com/joyent/illumos-joyent/blob/master/usr/src/uts/common/disp/cpucaps.c#L78-L102).


```
tenant.cpucaps.above_base_sec    # total time spent over baseline (s)
tenant.cpucaps.above_sec         # total time spent over CPU cap (s)
tenant.cpucaps.baseline          # CPU allocation for "normal" usage
tenant.cpucaps.below_sec         # total time spent under CPU cap (s)
tenant.cpucaps.burst_limit_sec   # how long this zone can burst (s)
tenant.cpucaps.bursting_sec      # how long the zone has been bursting (s)
tenant.cpucaps.effective         # are we using burst cap or or baseline
tenant.cpucaps.maxusage          # maximum observed CPU usage
tenant.cpucaps.nwait             # number of threads on cap wait queue
tenant.cpucaps.usage             # current aggregated CPU usage for all
                                 # threads, (%age of single CPU)
tenant.cpucaps.value             # cap value (%age of single CPU)

tenant.lockedmem.usage           # the amount of locked memory you have (b)
tenant.lockedmem.value           # the locked memory you can have (b)

tenant.nprocs.usage              # number of process running
tenant.nprocs.value              # maximum number of process you can run

tenant.physicalmem.usage         # how much RAM the zone is using (b)
tenant.physicalmem.value         # how much RAM the zone can use (b)

tenant.swapresv.usage            # how much swap the zone is using (b)
tenant.swapresv.value            # how much swap the zone can use (b)
```

I think nearly everything in the `memory_cap` kstat module should be
considered a rate. Only `rss` and `swap` appear to be genuine gauges
(i.e. they go down as well as up.) It's probably useful to have `nover`
as a gauge too though: it maybe useful to know how many times you've
been "over limit".

For now, the collector presents these metrics "as-is".

```
tenant.memory_cap.rss    # the resident set size of all procs in the zone
tenant.memory_cap.swap   # the amount of swap your zone is using
tenant.memory_cap.nover  # how many times your RSS has exceeded its cap
```

```
tenant.memory_cap.anon_alloc_fail
tenant.memory_cap.anonpgin
tenant.memory_cap.execpgin
tenant.memory_cap.fspgin
tenant.memory_cap.n_pf_throttle
tenant.memory_cap.n_pf_throttle_usec
tenant.memory_cap.pagedout
tenant.memory_cap.pgpgin
tenant.memory_cap.physcap
tenant.memory_cap.swapcap
```
