#!/bin/sh

# Script to run Experiment 2 with a combination of TCP variant pairs

rm -rf nam_files trace_files
mkdir nam_files trace_files

for cbr_rate in $(seq 0.1 0.1 10)
do
   ns xp2.tcl $cbr_rate"mb" "nam_files/out_"$cbr_rate"_a.nam" "trace_files/out_"$cbr_rate"_a.tr" TCP/Newreno TCP/Vegas 0.0
done


#Introduce a delay between TCP and CBR flows
for cbr_rate in $(seq 0.1 0.1 10)
do
   ns xp2.tcl $cbr_rate"mb" "nam_files/out_"$cbr_rate"_b.nam" "trace_files/out_"$cbr_rate"_b.tr" TCP/Newreno TCP/Vegas 1.0
done


