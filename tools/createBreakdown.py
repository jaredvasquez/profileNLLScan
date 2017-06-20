#!/usr/bin/env python
import os
import sys
import yaml
import ROOT as r
import numpy as np
from math import sqrt
from collections import OrderedDict
from scipy.optimize import root, fsolve, minimize

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

  for error in ['TOTAL','THEO','STAT']:
    # Get points
    # ---------------------------------------------------------------
    minNLL, pts = -999, []
    muhat = 1.0

    tc = r.TChain('nllscan')
    dirPATH = 'output/%s/%s/%s' % (ModelName,POIName,error)
    for i in xrange(npts):
      filepath = os.path.join(dirPATH,'result_%d.root'%i)
      if not os.path.isfile(filepath):
        print '   WARNING:: File %s does not exist' % filepath
      else:
        tc.AddFile(filepath)

    npts = tc.GetEntries()

    for ievt in xrange(npts):
      tc.GetEntry(ievt)
      poiVal = getattr(tc,POIName)
      if (ievt==0):
        minNLL = tc.nll
      if (ievt == 0 and error == 'TOTAL'):
        muhat = poiVal
      if tc.status:
        print 'WARNING : FIT FAILED @ %s = %f. Skipping Point.' % (POIName, poiVal), error
        continue
      pts.append( (poiVal, 2*(tc.nll-minNLL)) )

    pts.sort( key=lambda tup: tup[0] )
    xmin = min(pts,key=lambda x:x[0])[0]
    xmax = max(pts,key=lambda x:x[0])[0]


    # Fill TGraphs
    # ---------------------------------------------------------------
    tg = r.TGraph()
    for i in xrange(len(pts)):
      tg.SetPoint( i, pts[i][0], pts[i][1] )


    # Get spline and find 1 sigma and 2 sigma intercepts
    # ---------------------------------------------------------------
    sp = r.TSpline3('s',tg)
    width = (xmax-xmin)
    x0  = root(lambda x : sp.Eval(x), x0=muhat).x[0]
    x1p = root(lambda x: np.abs(1 - sp.Eval(x)), x0=(xmax - 0.2*width)).x[0]
    x1m = root(lambda x: np.abs(1 - sp.Eval(x)), x0=(xmin + 0.2*width)).x[0]

    err = [ abs(x0-x1p), -abs(x0-x1m) ]

    #print error
    #print ' %20s = %.2f +/- (%+.2f, %+.2f)' % ( POIName, x0, err[0], err[1] )
    results[POIName][error] = ( x0, err[0], err[1] )

    POITitle = POITitle.replace('#','\\')
    line = '%20s = %.2f^{%+.2f}_{%+.2f} \\\\' % ( POITitle, x0, err[0], err[1] )
    table.append( line )


## Print output

template  = '%s &= %.2f\ ^{%+.2f}_{%+.2f}'
template += ' = %.2f\ ^{%+.2f}_{%+.2f}\,\mathrm{(stat.)}'
template += '\ ^{%+.2f}_{%+.2f}\,\mathrm{(exp.)}'
template += '\ ^{%+.2f}_{%+.2f}\,\mathrm{(theory)}\\\\'

for POIName in pois:
  x0,  totHI,  totLO = results[POIName]['TOTAL']
  x0,  sthHI,  sthLO = results[POIName]['THEO']
  _,  statHI, statLO = results[POIName]['STAT']

  status = ''
  if (abs(sthHI) > abs(totHI) or abs(sthLO) > abs(totLO) or abs(statHI) > abs(sthHI) or abs(statLO) > abs(sthLO)):
    status = '***'

  expHI =  sqrt( abs( totHI**2 - sthHI**2 ) )
  expLO = -sqrt( abs( totLO**2 - sthLO**2 ) )

  theoHI =  sqrt( abs( sthHI**2 - statHI**2 ) )
  theoLO = -sqrt( abs( sthLO**2 - statLO**2 ) )

  title = pois[POIName][2].replace('#','\\')
  if POIName in replace: POIName = replace[POIName]
  print template % ( title, x0, totHI, totLO, x0, statHI, statLO, expHI, expLO, theoHI, theoLO), status


#print ''
#print 'Latex Formatted: \n'
#for line in table: print line
#print ''

