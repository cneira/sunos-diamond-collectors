# ZFS

Uses the `zfs` CLI to report on ZFS filesystems. Written
and tested on Solaris, but will likely work on FreeBSD and, if you
must, Linux.

Metric paths begin with `zfs.dataset`, to keep them cleanly
separated from ARC stats.

Dataset names have slashes converted to dots. So the `compressratio`
metric for the `tank/users/rob` dataset will be under
`zfs.dataset.tank.users.rob.compressratio`.

## Options

* **`datasets`**: a list of datasets on which to report. This can be
  a list of literal strings or of regular expressions. (See
  `regex`.) If you use regular expressions, Python's `match()`
  method is used so, for instance `db` would match everything in
  the `db` pool as well as `tank/db` and `space/users/redbeard`. So,
  remember to restrict your matches with metacharacters.
* **`regex`**: tells the collector whether or not to treat tha
  elements of `datasets` as literal strings or Python regexes.
* **`fields`**: a list of metrics you wish to collect.
  In common with all my other collectors, the magic value `__all__`
  matches everything. In this case "everything" is taken to mean
  anything in the output of `zfs get all <dataset>` where the value
  begins with a number. SI suffixes a
* **`counts`**: the collector is able to report the number of child
  datasets (`filesystem`), the number of `snapshot`s, and the number of
  `volume`s in a dataset. Only direct ancestors of the dataset are
  counted: it's *not* recursive.

## Statistics

This collector can take a long time to run. If you have many
hundreds of datasets, collection time may be in the seconds.
Consider the utility of the metrics, and only ask for what you need.
The nature of the collector, however, means you are not likely to
run it with a high frequency.

## Metric Paths

These are `__all__` auto-discovered metrics for a Solaris 11.3
dataset.

```
zfs.dataset.<dataset>.available
zfs.dataset.<dataset>.usedbydataset
zfs.dataset.<dataset>.referenced
zfs.dataset.<dataset>.version
zfs.dataset.<dataset>.usedbysnapshots
zfs.dataset.<dataset>.copies
zfs.dataset.<dataset>.compressratio
zfs.dataset.<dataset>.used
zfs.dataset.<dataset>.usedbyrefreservation
zfs.dataset.<dataset>.recordsize
zfs.dataset.<dataset>.usedbychildren
```

These are the additional `count` metrics.

```
zfs.count.<dataset>.filesystem
zfs.count.<dataset>.volume
zfs.count.<dataset>.snapshot
```
