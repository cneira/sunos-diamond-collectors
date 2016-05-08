# Zpool

Uses the `zpool` CLI to report on the state of ZFS pools. Written
and tested on Solaris, but will likely work on FreeBSD and, if you
must, Linux.

## Options

* **`fields`**: a list of metrics you wish to collect. For all
  metrics, use the magic value `__all__`.

## Statistics

Collecting information on four pools on an 8-core i7 system takes
around 15ms.

## Metric Paths

By default it reports all the columns in the default `zpool` output.
Namely:

`zpool.<pool>.size` (bytes)
`zpool.<pool>.alloc` (bytes)
`zpool.<pool>.free` (bytes)
`zpool.<pool>.cap` (float)
`zpool.<pool>.dedup` (float)

You can choose any subset of these via the `fields` configuration
setting.

Additionally, the health of the pool is reported, as an integer.

`zpool.<pool>.health` (int)

The values for this metric are:

* 0: `ONLINE`
* 1: `DEGRADED`
* 2: `SUSPENDED`
* 3: `UNAVAIL`
* 4: uknown state
