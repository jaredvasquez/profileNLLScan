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

    opts = [
      '-a 0-%d' % npoints,
      '--export=\"ATLAS_LOCAL_ROOT_BASE\"',
      '--job-name=%s_%s' % (options['ModelName'],poi),
      '--output=\"logs/%s_%s-%%a.log\"' % (options['ModelName'],poi),
      ]

    cmd = 'sbatch {options} ./scripts/jobFit.sh {config} {poi}'
    cmd = cmd.format( options=' '.join(opts), config=filePATH, poi=poi )
    jobid = commands.getstatusoutput(cmd)[1].split()[-1]
    print 'Dependency for jobid', jobid


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
