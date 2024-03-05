@echo off
REM Command-line parameters
set circuit=supremacy
set precision=double
set nreps_a=20
set nreps_b=3
set nreps_c=1
set filename_a=cpunithsimple.dat
set filename_b=gpunithsimple.dat

for /l %%nqubits in (1,1,30) do (
  echo %%nqubits
  set "CUDA_VISIBLE_DEVICES="
  python compare.py --circuit %circuit% --nqubits %%nqubits --filename %filename_b% ^
                    --library-options backend=qibojit,platform=numba,expectation="any_string_for_now" ^
                    --nreps %nreps_b% --precision %precision%
  echo.
)
