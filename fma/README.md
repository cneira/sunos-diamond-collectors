# FMA Collector

This is a very vague, experimental collector for the Solaris fault
management architecture. I'm not sure yet what it is worth
recording, and how, so this is almost certainly subject to change.

The collector uses the `fmadm` and `fmstat` commands to get its
information. They both require elevated privileges. The following
will work on Solaris 11.

Create a new `System Telemetry` profile.

```
$ cat >/etc/security/prof_attr.d/diamond
System Telemetry:RO::\
Allow access to system telemetry commands:
```
```
$ cat >/etc/security/exec_attd.d/diamond
System Telemetry:solaris:cmd:RO::/usr/sbin/fmstat:privs=sys_admin
System Telemetry:solaris:cmd:RO::/usr/sbin/fmadm:privs=sys_admin
```

Then grant the profile to the `diamond` user:

```
# usermod -P 'System Telemetry' diamond
```

## Metrics

There are two collectors in here. The first, `fmadm` looks for
faults, and groups them by the first part of their FMRI. So, if you
have two failing services, you will see a `.fma.fmadm.svc` metric
with a value of `2`.

```
fma.fmadm.<scheme>
```

The second metrics are attached to the `.fma.fmstat` path, and
duplicate the output of `fmstat`. Buffer and memory sizes are
converted to bytes. The `%w` and `%b` columns are renamed `pc_w` and
`pc_b` respectively.

```
fma.fmstat.<module>.ev_recv 0
fma.fmstat.<module>.ev_acpt 0
fma.fmstat.<module>.wait 0
fma.fmstat.<module>.svc_t 0
fma.fmstat.<module>.pc_w 0
fma.fmstat.<module>.pc_b 0
fma.fmstat.<module>.open
fma.fmstat.<module>.solve
fma.fmstat.<module>.memsz
fma.fmstat.<module>.bufsz
```

Where `<module>` is `sas-cabling`, `sensor-transport` etc.

## Options

The user can enable/disable the `fmadm` and/or `fmstat` parts of the
collector with `fmadm = True|False` settings.
