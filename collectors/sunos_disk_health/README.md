# Disk Health Collector


Uses the `kstat` interface to get error counts for physical disks.
errors for each disk.

The raw `kstat` counter values are used: the collector itself *does not*
compute rates or deltas.

## Options

* **`devices`**: a list of devices. Can be strings or regexes. By
  default, anything which identifies as a `disk`, (by means of having
  `disk` class kstats) will be included.

  To see your disks, run

  ```sh
  $ iostat -er
  ```

  By default, uses the magic value `__all__`, which collects information
  for anything identifying with the `device_error` kstat class.
* **`fields`**: In addition to Diamonds `metrics_whitelist` and
  `metrics_blacklist` configuration, you can use the `fields` variable
  to supply a filter list of fields which you are interested in.  A
  metric will only be published if its name is an element of that array.

  By default the collector looks for `hard_errors`, `soft_errors`,
  `transport_errors`, `device_not_ready` and `illegal_request`. You
  almost certainly don't want to look at `size`.
* **`sn_tag`**: If you are using a backend and a handler which supports
  points tags. (like Wavefront), you can choose to have the points
  tagged with information which makes the disks more easily
  identifiable. The collector will look for kstats which hold the disk's
  serial number, model, and manufacturer. If any or all of these are
  found, they are used as point tags. To disable, set this parameter to
  `False`. (bool)

To black/whitelist metrics, you must supply the device. For instance:

```
metrics_whitelist: cmdk0.hard_errors
```

### Examples

Collect all disk error information for all SATA devices, but disabling
point tags.

```
[[ SunOSDiskHealthCollector ]]
enabled = True
devices = __all__
sn_tag = False
```

Collect hard and soft errors for SAS disks, tagging them with their serial
numbers.

```
[[ SunOSDiskHealthCollector ]]
enabled = True
devices = sd[0-9]+
fields = hard_errors,soft_errors
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
