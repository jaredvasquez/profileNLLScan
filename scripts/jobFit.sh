#!/bin/sh

cd ~/hsg7root/quickFit/
source ./setup.sh
cd $SLURM_SUBMIT_DIR/

cmd="./tools/fitPoint.py $@ $SLURM_ARRAY_TASK_ID"
echo $cmd
$cmd
