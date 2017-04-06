#!/usr/bin/env python
import os
import sys
import yaml

if len(sys.argv) <= 1:
  print 'Please specify a config file.'
  sys.exit()

config = yaml.safe_load(open(sys.argv[1]))
options = config['Options']
pois = config['ParametersOfInterest']

usepoi = sys.argv[2]
ipoint = int(sys.argv[3])
fitrange = '1_-8_8'

xmin = pois[usepoi][0]
xmax = pois[usepoi][1]
npoint = options['NPoints']
fixval = (ipoint-1)*(xmax-xmin)/float(npoint) + xmin
if not ipoint: fixval=fitrange

poivals = [ '%s=%s' % (poi,fixval) if (poi==usepoi) else '%s=%s' % (poi,fitrange) for poi in pois ]
options['pois'] = ','.join(poivals)

outDir = 'output/%s/%s' % (options['ModelName'], usepoi)
outPATH = os.path.join(outDir,'result_%d.root'%ipoint)
os.system('mkdir -p %s' % outDir)

#cmd = "quickFit -f {file} -d {dataset} -p {pois} -n ATLAS_* -o {output}"
cmd = "quickFit -f {file} -d {dataset} -p {pois} -o {output}"
cmd = cmd.format( file=options['InputFile'], dataset=options['Dataset'], pois=options['pois'], output=outPATH )
os.system( cmd )
