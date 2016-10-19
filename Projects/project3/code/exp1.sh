#!/bin/sh
# Script to Run experiment 1 with various CBR Rates
rm -rf nam_files trace_files
mkdir nam_files trace_files

# Increment CBR by 0.1, run expriement and store in appropriate files
for cbr_rate in $(seq 0.1 0.1 10)
do
   ns xp1.tcl $cbr_rate"mb" "nam_files/out_"$cbr_rate"_a.nam" "trace_files/out_"$cbr_rate"_a.tr" TCP 0.0
done


# Increment CBR by 0.1, introduce a delay between TCP and CBR, run expriement and store in appropriate files
for cbr_rate in $(seq 0.1 0.1 10)
do
   ns xp1.tcl $cbr_rate"mb" "nam_files/out_"$cbr_rate"_a.nam" "trace_files/out_"$cbr_rate"_a.tr" TCP 1.0
done


