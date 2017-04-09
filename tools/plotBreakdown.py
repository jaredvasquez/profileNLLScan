#!/usr/bin/env python
import os
import sys
import yaml
import ROOT as r
import numpy as np
from scipy.optimize import root, fsolve

r.gStyle.SetOptStat(0)

fitsets = ['TOTAL','THEO','STAT']

# fix TLatex from making everything bold
# ---------------------------------------------------------------
def DrawNDC(self, x, y, text): self.DrawLatexNDC( x, y, '#bf{ %s }' % text )
r.TLatex.DrawNDC = DrawNDC


# Prepare TGraphs
#scolors = [None, r.kGreen-9, r.kYellow-9]
col = r.kGray+1
scolors = [None, col, col]
lcolors = [r.kBlack, r.kBlue, r.kRed]
tg = [ r.TGraph() for i in xrange(3) ]
for i in xrange(3):
  tg[i].SetLineColor(lcolors[i])
  tg[i].SetLineWidth(1)


# Get User Arguments
# ---------------------------------------------------------------
if (len(sys.argv) <= 2):
  print '%s Config POIName' % sys.argv[0]; sys.exit()

config = yaml.safe_load(open(sys.argv[1]))
options = config['Options']

npts = options['NPoints']
ModelName = options['ModelName']
POIName = sys.argv[2]
POITitle = config['ParametersOfInterest'][POIName][2]


# Get points
# ---------------------------------------------------------------
ymax = 1.2
for iset, fitset in enumerate(fitsets):
  minNLL = -999
  pts = []

  tc = r.TChain('nllscan')
  dirPATH = 'output/%s/%s/%s' % (ModelName,POIName, fitset)
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
  imax = max(pts,key=lambda x:x[1])[1]
  if (imax > ymax and imax <= 6): ymax = imax

  # Fill TGraphs
  # ---------------------------------------------------------------
  for i in xrange(len(pts)): tg[iset].SetPoint( i, pts[i][0], pts[i][1] )


# Get spline and find 1 sigma and 2 sigma intercepts
# ---------------------------------------------------------------
sp = r.TSpline3('s',tg[0])
x0  = root(lambda x : sp.Eval(x), x0=1.0).x[0]
#x2p = root(lambda x: np.abs(4 - sp.Eval(x)), x0=xmax).x[0]
#x2m = root(lambda x: np.abs(4 - sp.Eval(x)), x0=xmin).x[0]
x1p = root(lambda x: np.abs(1 - sp.Eval(x)), x0=xmax).x[0]
x1m = root(lambda x: np.abs(1 - sp.Eval(x)), x0=xmin).x[0]
xbs = [ None, (x1m,x1p) ] #, (x2m,x2p) ]
errors = [ ( abs(x0-x1p), -abs(x0-x1m) ) ]

print ' %s = %.3f +/- (%.3f,%.3f) \n' % ( POIName, x0, errors[0][0], errors[0][1] )
#print ' %s = %.3f +/- (%.3f,%.3f) ++/-- (%.3f,%.3f) \n' % ( POIName, x0, errors[0][0], errors[0][1], errors[1][0], errors[1][1] )

# Prep the canvas
# ---------------------------------------------------------------
can = r.TCanvas()
can.cd()
can.SetMargin( 0.10, 0.05, 0.13, 0.15 )
h = r.TH1F('hist','',npts,xmin,xmax)
h.SetMaximum(ymax+0.01)
h.SetMinimum(1e-06)
#h.GetXaxis().SetTitle('#mu')
#h.GetYaxis().SetTitle('#lambda(#mu)')
h.GetXaxis().SetTitle(POITitle)
h.GetYaxis().SetTitle('-2 ln #Lambda')
h.GetYaxis().SetTitleOffset(0.7)
h.GetXaxis().SetTitleSize(0.05)
h.GetYaxis().SetTitleSize(0.05)
h.Draw('HIST')


# Draw guides
# ---------------------------------------------------------------
tl = r.TLine()
tt = r.TLatex()
tl.SetLineStyle(2)

#colors = [None, r.kGreen-3, r.kOrange-2]
colors = [None, col, col]
for i in xrange(1,3):
  tt.SetTextColor( colors[i] )
  tl.SetLineColor( colors[i] )
  if (i==1 or ymax > 4):
    tt.DrawLatex( xmin + 0.92*(xmax-xmin), i**2-0.35, '%d #sigma' % i)
    tl.DrawLine( xmin, i**2, xmax, i**2 )
  if (i==1):
    if (xmin < xbs[i][0]): tl.DrawLine( xbs[i][0], 0, xbs[i][0], ymax )
    if (xmax > xbs[i][1]): tl.DrawLine( xbs[i][1], 0, xbs[i][1], ymax )


# Draw contours
# ---------------------------------------------------------------
tg[2].Draw('C SAME')
tg[1].Draw('C SAME')
tg[0].SetMarkerStyle(20)
tg[0].SetMarkerSize(0.4)
tg[0].Draw('PC SAME')


# Draw more guides
# ---------------------------------------------------------------
tl.SetLineColor(r.kBlack)
r.gStyle.SetLineStyleString(11,'15 45');
for i in xrange( int(xmin), int(xmax)+1 ):
  if (i==1):
    tl.SetLineWidth(1)
    tl.SetLineStyle(3)
  else:
    tl.SetLineWidth(1)
    tl.SetLineStyle(11)
  tl.DrawLine( i, 0, i, ymax )

tl.SetLineWidth(1)
tl.SetLineStyle(1)
tl.DrawLine( x0, 0, x0, ymax )


# Label the plot
# ---------------------------------------------------------------
tt.SetTextSize(0.065)
tt.SetTextColor( r.kBlack )
tt.DrawNDC( 0.11, 0.93, '#bf{#it{ATLAS}} Internal' )
tt.SetTextSize(0.04)
tt.DrawNDC( 0.11, 0.875, '#it{H #rightarrow #gamma#gamma}, #it{m_{H}} = 125.09 GeV' )


# Draw Legend
# ---------------------------------------------------------------
tt.SetTextSize(0.051)
#tt.DrawNDC( 0.65, 0.94, 'Total Uncertainty' )
def drawLegItem( x, y, label, color ):
  tl.SetLineColor( color )
  tl.SetLineWidth(2)
  tl.DrawLineNDC( x, y, x+0.04, y)
  tt.DrawNDC( x+0.045, y-0.016, label)

leg1 = drawLegItem( 0.49, 0.92, 'Total',  lcolors[0] )
leg2 = drawLegItem( 0.64, 0.92, 'Theory', lcolors[1] )
leg2 = drawLegItem( 0.82, 0.92, 'Stat',   lcolors[2] )


# Tidy up and save output
# ---------------------------------------------------------------
h.Draw('AXIS SAME')

for ext in ['pdf']:
  os.system('mkdir -p plots/%s' % (ModelName) )
  can.SaveAs('plots/%s/%s.%s' % (ModelName,POIName,ext))


