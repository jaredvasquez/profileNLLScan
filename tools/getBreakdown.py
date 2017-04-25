#!/usr/bin/env python
import os
import sys
import yaml
import ROOT as r
import numpy as np
from math import sqrt
from collections import OrderedDict
from scipy.optimize import root, fsolve

# ---------------------------------------------------------------
replace = {
  'mu'     : '\mu',
  'mu_ggH' : '\mu_{ggH}',
  'mu_VBF' : '\mu_\mathrm{VBF}',
  'mu_WH'  : '\mu_\mathrm{WH}',
  'mu_ZH'  : '\mu_\mathrm{ZH}',
  'mu_ttH' : '\mu_{t\\bar{t}H}',
}


# ---------------------------------------------------------------
def ordered_load(stream, Loader=yaml.SafeLoader, object_pairs_hook=OrderedDict):
  class OrderedLoader(Loader):
    pass
  def construct_mapping(loader, node):
    loader.flatten_mapping(node)
    return object_pairs_hook(loader.construct_pairs(node))
  OrderedLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_mapping)
  return yaml.load(stream, OrderedLoader)


# Get User Arguments
# ---------------------------------------------------------------
if (len(sys.argv) <= 1):
  print '%s Config' % sys.argv[0]; sys.exit()

#config = yaml.safe_load(open(sys.argv[1]))
config = ordered_load(open(sys.argv[1]))
options = config['Options']

npts = options['NPoints']
ModelName = options['ModelName']
pois = config['ParametersOfInterest']

table = []

results = { p: {}  for p in pois }
for POIName in pois:
  POITitle = config['ParametersOfInterest'][POIName][2]

  for error in ['TOTAL','STAT']:
    # Get points
    # ---------------------------------------------------------------
    minNLL, pts = -999, []

    tc = r.TChain('nllscan')
    dirPATH = 'output/%s/%s/%s' % (ModelName,POIName,error)
    for i in xrange(npts): tc.AddFile( os.path.join(dirPATH,'result_%d.root'%i) )

    for ievt in xrange(npts):
      tc.GetEntry(ievt)
      poiVal = getattr(tc,POIName)
      if (ievt==0): minNLL = tc.nll
      if tc.status:
        print 'WARNING : FIT FAILED @ %s = %f. Skipping Point.' % (POIName, poiVal)
        continue
      pts.append( (poiVal, 2*(tc.nll-minNLL)) )

    pts.sort( key=lambda tup: tup[0] )
    xmin = min(pts,key=lambda x:x[0])[0]
    xmax = max(pts,key=lambda x:x[0])[0]


    # Fill TGraphs
    # ---------------------------------------------------------------
    tg = r.TGraph()
    for i in xrange(npts):
      tg.SetPoint( i, pts[i][0], pts[i][1] )


    # Get spline and find 1 sigma and 2 sigma intercepts
    # ---------------------------------------------------------------
    sp = r.TSpline3('s',tg)
    x0  = root(lambda x : sp.Eval(x), x0=1.0).x[0]
    x1p = root(lambda x: np.abs(1 - sp.Eval(x)), x0=xmax).x[0]
    x1m = root(lambda x: np.abs(1 - sp.Eval(x)), x0=xmin).x[0]
    err = [ abs(x0-x1p), -abs(x0-x1m) ]

    #print error
    #print ' %20s = %.2f +/- (%+.2f, %+.2f)' % ( POIName, x0, err[0], err[1] )
    results[POIName][error] = ( x0, err[0], err[1] )

    POITitle = POITitle.replace('#','\\')
    line = '%20s = %.2f^{%+.2f}_{%+.2f} \\\\' % ( POITitle, x0, err[0], err[1] )
    table.append( line )


## Print output

template  = '%20s &= %.2f\ ^{%+.2f}_{%+.2f}'
template += ' = %.2f\ ^{%+.2f}_{%+.2f}\,\mathrm{(stat.)}'
template += '\ ^{%+.2f}_{%+.2f}\,\mathrm{(syst.)}\\\\'

for POIName in pois:
  x0,  totHI,  totLO = results[POIName]['TOTAL']
  _,  statHI, statLO = results[POIName]['STAT']

  status = ''
  if (abs(statHI) > abs(totHI) or abs(statLO) > abs(totLO)):
    status = '***'

  expHI =  sqrt( abs( totHI**2 - statHI**2 ) )
  expLO = -sqrt( abs( totLO**2 - statLO**2 ) )

  if POIName in replace: POIName = replace[POIName]
  print template % ( POIName, x0, totHI, totLO, x0, statHI, statLO, expHI, expLO), status


#print ''
#print 'Latex Formatted: \n'
#for line in table: print line
#print ''

