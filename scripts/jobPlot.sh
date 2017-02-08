#!/bin/sh

cd $SLURM_SUBMIT_DIR/
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh  # setupATLAS
lsetup root

cmd="./tools/plotProfileLH.py $@ -b"
echo $cmd
$cmd
