# ZFS Arc

Takes ZFS arc kstats and turns them into metrics. Does not do the
renaming that the collectd equivalent does, which I think makes it
more future-proof.

Taking inspiration from (i.e. directly copying) [the Telegraf ZFS
plugin](https://github.com/influxdata/telegraf/tree/master/plugins/inputs/zfs)
we also collect metrics from the `vdev_cache_stats` and `zfetchstats` modules.

## Options

You can filter metrics using the standard Diamond whitelist/blacklist
configuration, but the following options are provided for greater
convenience.

* **`arcstats`** : a list of `arcstat` statistics you wish to collect.
  Regular expressions are not allowed. To collect all of them, use the
  magic value `__all__`, to collect none, use `__none__`.
* **`vdev_cache_stats`**:  Just like `arcstats`, but for the
  `vdev_cache_stats` kstats.
* **`zfetchstats`**:  Just like `arcstats`, but for the
  `zfetchstats` kstats.

### Examples

Collect all arcstats, but nothing else:

```
[[ ZFSArcCollector ]]
arcstats = __all__
vdev_cache_stats = __none__
zfetch_stats = __none__
```

## Bugs and Caveats

The kstat values are reported "raw": that is `crtime` and `snaptime` are
not used to calculate differentials. Your graphing software should
calculate rates, but they will not be as accurate as if they were
calculated from the high-resolution kstat times.

## Metric Paths

```
zfs.arcstats.buf_size
zfs.arcstats.c
zfs.arcstats.c_max
zfs.arcstats.c_min
zfs.arcstats.data_size
zfs.arcstats.deleted
zfs.arcstats.demand_data_hits
zfs.arcstats.demand_data_misses
zfs.arcstats.demand_metadata_hits
zfs.arcstats.demand_metadata_misses
zfs.arcstats.evict_l2_cached
zfs.arcstats.evict_l2_eligible
zfs.arcstats.evict_l2_ineligible
zfs.arcstats.evict_prefetch
zfs.arcstats.evicted_mfu
zfs.arcstats.evicted_mru
zfs.arcstats.hash_chain_max
zfs.arcstats.hash_chains
zfs.arcstats.hash_collisions
zfs.arcstats.hash_elements
zfs.arcstats.hash_elements_max
zfs.arcstats.hits
zfs.arcstats.l2_abort_lowmem
zfs.arcstats.l2_cksum_bad
zfs.arcstats.l2_feeds
zfs.arcstats.l2_hdr_size
zfs.arcstats.l2_hits
zfs.arcstats.l2_imports
zfs.arcstats.l2_io_error
zfs.arcstats.l2_misses
zfs.arcstats.l2_persistence_hits
zfs.arcstats.l2_read_bytes
zfs.arcstats.l2_rw_clash
zfs.arcstats.l2_size
zfs.arcstats.l2_write_bytes
zfs.arcstats.l2_writes_done
zfs.arcstats.l2_writes_error
zfs.arcstats.l2_writes_sent
zfs.arcstats.memory_throttle_count
zfs.arcstats.meta_limit
zfs.arcstats.meta_max
zfs.arcstats.meta_used
zfs.arcstats.mfu_ghost_hits
zfs.arcstats.mfu_hits
zfs.arcstats.misses
zfs.arcstats.mru_ghost_hits
zfs.arcstats.mru_hits
zfs.arcstats.mutex_miss
zfs.arcstats.other_size
zfs.arcstats.p
zfs.arcstats.prefetch_behind_prefetch
zfs.arcstats.prefetch_data_hits
zfs.arcstats.prefetch_data_misses
zfs.arcstats.prefetch_joins
zfs.arcstats.prefetch_meta_size
zfs.arcstats.prefetch_metadata_hits
zfs.arcstats.prefetch_metadata_misses
zfs.arcstats.prefetch_reads
zfs.arcstats.prefetch_size
zfs.arcstats.rawdata_size
zfs.arcstats.size
zfs.vdev_cache_stats.delegations
zfs.vdev_cache_stats.hits
zfs.vdev_cache_stats.misses
zfs.zfetchstats.arc_pf_throttle
zfs.zfetchstats.blocks_fetched
zfs.zfetchstats.dup_triggers
zfs.zfetchstats.fetched_cached
zfs.zfetchstats.hash_collisions
zfs.zfetchstats.interleaved_streams
zfs.zfetchstats.new_streams
zfs.zfetchstats.trigger_hits
zfs.zfetchstats.trigger_timeouts
zfs.zfetchstats.triggers_in_hash
zfs.zfetchstats.uncached_triggers
```
