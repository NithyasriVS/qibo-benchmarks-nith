#! /usr/bin/bash
# Command-line parameters
: "${circuit:=supremacy}"
: "${precision:=double}"
: "${nreps_a:=20}" # for nqubits < 25
: "${nreps_b:=3}"  # for nqubits >= 25
: "${nreps_c:=1}"  
: "${filename_a:=cpunithsimple.dat}"
: "${filename_b:=gpunithsimple.dat}"
 
for nqubits in {1..30}
do
echo $nqubits
  CUDA_VISIBLE_DEVICES="" python compare.py --circuit $circuit --nqubits $nqubits --filename $filename_b \
                                            --library-options backend=qibojit,platform=numba,expectation="any_string_for_now" \
                                            --nreps $nreps_b --precision $precision
  echo
done