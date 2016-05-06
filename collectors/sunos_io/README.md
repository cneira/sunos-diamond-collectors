# SunOS IO Collector

Uses the `kstat` interface to get disk IO statistics. The raw
`kstat` counter values are used: the collector itself *does not*
compute rates or deltas. This should be done by your graphing
software.

## Options

* **`devices`**: a list of devices. Can be strings or regexes.
* **`fields`**: a list of IO fields you want to collect. Refer to
  the [metric paths section](#metric-paths) below for a list of
  viable fields.

### Examples

Collect all available statistics for all `cmdk` devices.


```
[[ SunOSIOCollector ]]
enabled = True
devices = cmdk\d+
```

Collect bytes read and written on `cmdk1` and `cmdk2`.

```
[[ SunOSIOCollector ]]
enabled = True
fields = nread,nwritten
devices = cmdk1,cmdk2
```

## Statistics

Collecting all information for three devices on an 8-core i7 system
takes under 10ms.

## Metric Paths

You can find more information by reading [the relevant parts of the
illumos source
code](https://github.com/illumos/illumos-gate/blob/master/usr/src/uts/common/sys/kstat.h#L588-L685).

```
io.<disk>.nread     # number of bytes read
io.<disk>.nwritten  # number of bytes written
io.<disk>.rcnt      # count of elements in run state
io.<disk>.reads     # number of read operations
io.<disk>.wcnt      # count of elements in wait state
io.<disk>.writes    # number of write operations
```

The only pattern I've seen so far for `disk` is `cmdk[0-9]+`, but I
suspect there are `did`s out there, and possibly others I've not
thought of.
