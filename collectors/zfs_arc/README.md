# ZFS Arc

Takes ZFS arc kstats and turns them into metrics. Does not do the
renaming that the collectd equivalent does, which I think makes it
more future-proof.

By default all ARC stats are dumped. If you wish to be more
selective, you can supply a comma-separated list of the kstat names
you want. The names are the final parts of the paths listed below.

## Metric Paths

```
zfs.arc.buf_size
zfs.arc.c
zfs.arc.c_max
zfs.arc.c_min
zfs.arc.data_size
zfs.arc.deleted
zfs.arc.demand_data_hits
zfs.arc.demand_data_misses
zfs.arc.demand_metadata_hits
zfs.arc.demand_metadata_misses
zfs.arc.evict_l2_cached
zfs.arc.evict_l2_eligible
zfs.arc.evict_l2_ineligible
zfs.arc.evict_prefetch
zfs.arc.evicted_mfu
zfs.arc.evicted_mru
zfs.arc.hash_chain_max
zfs.arc.hash_chains
zfs.arc.hash_collisions
zfs.arc.hash_elements
zfs.arc.hash_elements_max
zfs.arc.hits
zfs.arc.l2_abort_lowmem
zfs.arc.l2_cksum_bad
zfs.arc.l2_feeds
zfs.arc.l2_hdr_size
zfs.arc.l2_hits
zfs.arc.l2_imports
zfs.arc.l2_io_error
zfs.arc.l2_misses
zfs.arc.l2_persistence_hits
zfs.arc.l2_read_bytes
zfs.arc.l2_rw_clash
zfs.arc.l2_size
zfs.arc.l2_write_bytes
zfs.arc.l2_writes_done
zfs.arc.l2_writes_error
zfs.arc.l2_writes_sent
zfs.arc.memory_throttle_count
zfs.arc.meta_limit
zfs.arc.meta_max
zfs.arc.meta_used
zfs.arc.mfu_ghost_hits
zfs.arc.mfu_hits
zfs.arc.misses
zfs.arc.mru_ghost_hits
zfs.arc.mru_hits
zfs.arc.mutex_miss
zfs.arc.other_size
zfs.arc.p
zfs.arc.prefetch_behind_prefetch
zfs.arc.prefetch_data_hits
zfs.arc.prefetch_data_misses
zfs.arc.prefetch_joins
zfs.arc.prefetch_meta_size
zfs.arc.prefetch_metadata_hits
zfs.arc.prefetch_metadata_misses
zfs.arc.prefetch_reads
zfs.arc.prefetch_size
zfs.arc.rawdata_size
zfs.arc.size
```
