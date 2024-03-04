#! /usr/bin/bash
# Generates data for qibotn breakdown bar plot with dry run vs simulation

# Command-line parameters
: "${filename:=qibotn_breakdown.dat}"
: "${precision:=double}"
: "${circuit:=supremacy}"
: "${nreps_cpu:=5}"
: "${nreps_gpu:=10}"


for nqubits in 16 18 20 22 24 26 28
do
    CUDA_VISIBLE_DEVICES=0 python compare.py --circuit $circuit --nqubits $nqubits --filename $filename \
                                             --library-options backend=qibotn,platform=cuquantum --nreps $nreps_gpu --precision $precision
    echo
    CUDA_VISIBLE_DEVICES="" python compare.py --circuit $circuit --nqubits $nqubits --filename $filename \
                                              --library-options backend=qibotn,platform=quimb --nreps $nreps_cpu --precision $precision
    echo
done
