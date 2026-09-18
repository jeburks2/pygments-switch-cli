# Cisco NX-OS

Aliases: `nxos`, `nx-os`, `cisco-nxos`, `nexus` · Filenames: `*.nxos`

NX-OS configuration for Nexus switches, including the `feature` lines,
`vn-segment` VLAN mappings and `nve` overlay interfaces that make up a
VXLAN EVPN fabric. Storage and virtual interface types (`fc1/1`, `vfc1`,
`Vethernet1`, `Bdi100`, `san-port-channel1`) are recognized as well.

`switchname`, `nv overlay evpn`, `vpc domain` and `feature …` lines drive
`analyse_text`.

```nxos
--8<-- "examples/nxos.nxos"
```
