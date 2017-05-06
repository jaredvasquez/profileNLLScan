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
errors = sys.argv[3]
ipoint = int(sys.argv[4])
fitrange = '1_-8_8'

xmin = pois[usepoi][0]
xmax = pois[usepoi][1]
npoint = options['NPoints']
fixval = (ipoint-1)*(xmax-xmin)/float(npoint) + xmin
if not ipoint: fixval=None #fitrange

#poivals = [ '%s=%s' % (poi,fixval) if (poi==usepoi) else '%s=%s' % (poi,fitrange) for poi in pois ]
poivals = [ '%s=%s' % (poi,fixval) if (poi==usepoi and fixval != None) else '%s' % (poi) for poi in pois ]
options['pois'] = ','.join(poivals)

outDir = 'output/%s/%s/%s' % (options['ModelName'], usepoi, errors)
outPATH = os.path.join(outDir,'result_%d.root'%ipoint)
os.system('mkdir -p %s' % outDir)

#cmd = "quickFit -f {file} -d {dataset} -p {pois} -n ATLAS_* -o {output}"

cmd = "quickFit -f {file} -d {dataset} -p {pois} -o {output}"
cmd = cmd.format( file=options['InputFile'], dataset=options['Dataset'], pois=options['pois'], output=outPATH )
if 'Tolerance' in options:
  cmd += ' --minTolerance %E' % (options['Tolerance'])
if 'Snapshot' in options:
  cmd += (' -s %s' % options['Snapshot'])

if   errors == 'STAT':
  cmd += ' -n ATLAS_*'

elif errors == 'THEO':
  cmd += ' -n ATLAS_EG_*,ATLAS_EL_*,ATLAS_FT_*,ATLAS_Hgg_*,ATLAS_JET_*,'
  cmd +=     'ATLAS_MET_*,ATLAS_MSS_*,ATLAS_MUON_*,ATLAS_PH_*,ATLAS_PRW_*,ATLAS_lumi*,ATLAS_HF*'

print(cmd)
print ''
os.system( cmd )
