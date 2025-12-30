#!/usr/bin/env gw_sh

# Simple script for running synthesis and flashing
# the board with generated bitstream

# synthesize HDL
open_project hdl.gprj
run all

# flash bitstream to RAM
set cmd [exec openFPGALoader impl/pnr/hdl.fs]
puts $cmd
