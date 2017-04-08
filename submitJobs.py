#!/usr/bin/env python
import os
import sys
import yaml
import commands

#------------------------------------------------------------------------------
def submitFile( filePATH ):
  config = yaml.safe_load(open(filePATH))
  options = config['Options']
  pois = config['ParametersOfInterest']

  npoints = options['NPoints']+2
  for poi in pois:

    for errors in ['TOTAL','THEO','STAT']:
      # Submit fit jobs
      opts = [
        '-t 0-%d' % npoints,
        '-N %s_%s_%s' % (options['ModelName'],poi, errors),
      ]
      cmd = 'qsub -q hep {options} ./scripts/jobFit.pbs -F \"{config} {poi} {errors}\"'
      cmd = cmd.format( options=' '.join(opts), config=filePATH, poi=poi, errors=errors )
      os.system(cmd)

#------------------------------------------------------------------------------
if __name__ == "__main__":
  if len(sys.argv) <= 1:
    print 'Please specify a config file.'
    sys.exit()

  inpath = sys.argv[1]

  if os.path.isfile(inpath):
    submitFile( inpath )

  elif os.path.isdir(inpath):
    for fname in os.listdir(inpath):
      submitFile( os.path.join(inpath,fname) )

  else:
    print 'Must specify input config file or directory'
