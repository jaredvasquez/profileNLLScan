#!/usr/bin/env python
import os
import sys
import yaml
import ROOT as r
import numpy as np
from scipy.optimize import root, fsolve

r.gStyle.SetOptStat(0)

# fix TLatex from making everything bold
# ---------------------------------------------------------------
def DrawNDC(self, x, y, text): self.DrawLatexNDC( x, y, '#bf{ %s }' % text )
r.TLatex.DrawNDC = DrawNDC


# Prepare TGraphs
# ---------------------------------------------------------------
scolors = [None, r.kGreen-9, r.kYellow-9]
tg = [ r.TGraph() for i in xrange(3) ]
for i in xrange(3):
  tg[i].SetLineColor(r.kBlack)
  tg[i].SetLineWidth(1)
  if scolors[i]: tg[i].SetFillColor( scolors[i] )


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
minNLL = -999
ymax = 6.0
pts = []

tc = r.TChain('nllscan')
dirPATH = 'output/%s/%s/' % (ModelName,POIName)
for i in xrange(npts): tc.AddFile( os.path.join(dirPATH,'result_%d.root'%i) )

for ievt in xrange(npts):
  tc.GetEntry(ievt)
  poiVal = getattr(tc,POIName)
  if (ievt==0): minNLL = tc.nll
  if tc.status:
    print 'WARNING : FIT FAILED @ %f. Skipping Point.' % poiVal
    continue
  pts.append( (poiVal, 2*(tc.nll-minNLL)) )

pts.sort( key=lambda tup: tup[0] )
xmin = min(pts,key=lambda x:x[0])[0]
xmax = max(pts,key=lambda x:x[0])[0]


# Fill TGraphs
# ---------------------------------------------------------------
for i in xrange(npts): tg[0].SetPoint( i, pts[i][0], pts[i][1] )


# Get spline and find 1 sigma and 2 sigma intercepts
# ---------------------------------------------------------------
sp = r.TSpline3('s',tg[0])
x0  = root(lambda x : sp.Eval(x), x0=1.0).x[0]
x2p = root(lambda x: np.abs(4 - sp.Eval(x)), x0=xmax).x[0]
x2m = root(lambda x: np.abs(4 - sp.Eval(x)), x0=xmin).x[0]
x1p = root(lambda x: np.abs(1 - sp.Eval(x)), x0=xmax).x[0]
x1m = root(lambda x: np.abs(1 - sp.Eval(x)), x0=xmin).x[0]
xbs = [ None, (x1m,x1p), (x2m,x2p) ]
errors = [ ( abs(x0-x1p), -abs(x0-x1m) ), ( abs(x0-x2p), -abs(x0-x2m) ) ]

print ' mu = %.3f +/- (%.3f,%.3f) ++/-- (%.3f,%.3f) \n' % ( x0, errors[0][0], errors[0][1], errors[1][0], errors[1][1] )

# Make 1 sigma and 2 sigma bands
# ---------------------------------------------------------------
n = 501
xs = np.linspace(x1m,x1p,n)
for i in xrange(n):
  tg[1].SetPoint( i,   xs[i],  sp.Eval(xs[i]) )
  tg[1].SetPoint( n+i, xs[n-i-1], ymax )

n = 501
xs = np.linspace(x2m,x2p,n)
for i in xrange(n):
  tg[2].SetPoint( i,   xs[i],  sp.Eval(xs[i]) )
  tg[2].SetPoint( n+i, xs[n-i-1], ymax )


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
h.GetYaxis().SetTitle('-2#Delta#mathcal{L}')
h.GetYaxis().SetTitleOffset(0.7)
h.GetXaxis().SetTitleSize(0.05)
h.GetYaxis().SetTitleSize(0.05)
h.Draw('HIST')


# Draw guides
# ---------------------------------------------------------------
tl = r.TLine()
tt = r.TLatex()
tl.SetLineStyle(2)

colors = [None, r.kGreen-3, r.kOrange-2]
for i in xrange(1,3):
  tt.SetTextColor( colors[i] )
  tl.SetLineColor( colors[i] )
  if (xmax > xbs[i][1]):
    tt.DrawLatex( xmin + 0.92*(xmax-xmin), i**2-0.35, '%d #sigma' % i)
  tl.DrawLine( xmin, i**2, xmax, i**2 )
  if (i==1):
    if (xmin < xbs[i][0]): tl.DrawLine( xbs[i][0], 0, xbs[i][0], ymax )
    if (xmax > xbs[i][1]): tl.DrawLine( xbs[i][1], 0, xbs[i][1], ymax )


# Draw contours
# ---------------------------------------------------------------
tg[2].Draw('F SAME')
tg[1].Draw('F SAME')
tg[0].Draw('C SAME')


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
tt.SetTextSize(0.055)
tt.DrawNDC( 0.65, 0.94, 'Total Uncertainty' )
def drawLegItem( x, y, label, color ):
  tp = r.TPave( x, y, x+0.04, y-0.05, 0, 'NDC' )
  tp.SetLineColor(r.kBlack)
  tp.SetFillColor( color )
  tp.Draw('NDC')
  tt.DrawNDC( x+0.045, y-0.04, label)
  return tp

leg1 = drawLegItem( 0.66, 0.92, '#pm 1#sigma', scolors[1] )
leg2 = drawLegItem( 0.79, 0.92, '#pm 2#sigma', scolors[2] )


# Tidy up and save output
# ---------------------------------------------------------------
h.Draw('AXIS SAME')

for ext in ['pdf']:
  os.system('mkdir -p plots/%s' % (ModelName) )
  can.SaveAs('plots/%s/%s.%s' % (ModelName,POIName,ext))


