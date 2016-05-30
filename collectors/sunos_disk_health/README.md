# Disk Health Collector


Uses the `kstat` interface to get error counts for physical disks.
errors for each disk.

The raw `kstat` counter values are used: the collector itself *does not*
compute rates or deltas.

## Options

* **`modules`**: I don't know what disks you have in your system. The
  Solaris 11 box I am working on right now has SATA disks accessed
  through the `cmdk` driver. My JPC zones have SAS drives, so use the
  `sd` driver. By default the collector looks for both these types using
  the `cmdkerror` and `sderr` kstat modules respectively. If you have
  something else, you can query it by adding to this variable.

  You can find out what your disks call themselves by running

  ```sh
  $ iostat -er
  ```

* **`fields`**: In addition to Diamonds `metrics_whitelist` and
  `metrics_blacklist` configuration, you can use the `fields` variable
  to supply a filter list of fields which you are interested in.  A
  metric will only be published if its name is an element of that array.

  By default the collector looks for `hard_errors`, `soft_errors`,
  `transport_errors`, `device_not_ready` and `illegal_request`. You
  almost certainly don't want to look at `size`.

To black/whitelist metrics, you must supply the device. For instance:

```
metrics_whitelist: cmdk0.hard_errors
```

### Examples

Collect all disk error information for all SATA devices.

```
[[ SunOSDiskHealthCollector ]]
enabled = True
modules = cmdkerror
```

## Metric Paths

```
disk.error.<device>.device_not_ready
disk.error.<device>.hard_errors
disk.error.<device>.illegal_request
disk.error.<device>.media_error
disk.error.<device>.no_device
disk.error.<device>.recoverable
disk.error.<device>.size
disk.error.<device>.soft_errors
disk.error.<device>.transport_errors
```
