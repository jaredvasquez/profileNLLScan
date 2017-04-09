#!/usr/bin/env python
import os
import sys
import yaml

# Get User Arguments
# ---------------------------------------------------------------
if (len(sys.argv) <= 1):
  print '%s Config' % sys.argv[0]; sys.exit()

fname = sys.argv[1]
config = yaml.safe_load(open(fname))
pois = config['ParametersOfInterest']
for poi in pois:
  cmd = './tools/plotBreakdown.py %s %s -b' % (fname, poi)
  print(cmd)
  os.system(cmd)
