#!/bin/sh

# script to run Experiment 3 with TCP varian and Queue type as input parameter

rm -rf nam_files trace_files
mkdir nam_files trace_files


ns xp3.tcl "nam_files/out_"$tcp_offset"_a.nam" "trace_files/out_"$tcp_offset"_a.tr" TCP/Sack1 RED








