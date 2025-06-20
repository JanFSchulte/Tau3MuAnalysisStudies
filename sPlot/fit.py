import ROOT
from setTDRStyle import setTDRStyle


def fitAndPlot(ws, obj, label, data=False):
	
	fitResult = ws.pdf("model").fitTo(ws.data("hist%sRoo"%obj), ROOT.RooFit.Save())


	c1 = ROOT.TCanvas("c1","c1",700,700)
	c1.cd()	
	plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)
	style = setTDRStyle()
	ROOT.gStyle.SetOptStat(0)
	plotPad.UseCurrentStyle()
	plotPad.Draw()	
	plotPad.cd()

	ws.var("mass").setBins(40)
	frame = ws.var('mass').frame(ROOT.RooFit.Title('Invariant mass of dimuon pairs'))
	frame.GetXaxis().SetTitle('m_{#mu#mu} [GeV]')
	frame.GetYaxis().SetTitle("Events / 0.01 GeV")
	ROOT.RooAbsData.plotOn(ws.data('hist%sRoo'%obj), frame,ROOT.RooFit.Name("hist%sRoo"%obj))
	ws.pdf('model').plotOn(frame,ROOT.RooFit.Name("model"))
	frame.Draw()


	latex = ROOT.TLatex()
	latex.SetTextFont(42)
	latex.SetTextAlign(31)
	latex.SetTextSize(0.04)
	latex.SetNDC(True)
	latexCMS = ROOT.TLatex()
	latexCMS.SetTextFont(61)
	latexCMS.SetTextSize(0.08)
	latexCMS.SetNDC(True)
	latexCMSExtra = ROOT.TLatex()
	latexCMSExtra.SetTextFont(52)
	latexCMSExtra.SetTextSize(0.045)
	latexCMSExtra.SetNDC(True) 
		
	latex.DrawLatex(0.95, 0.96, "(13.6 TeV)")

	if data:
		cmsExtra = "Preliminary"
	else:	
		cmsExtra = "#splitline{Simulation}{Preliminary}"
	latexCMS.DrawLatex(0.19,0.85,"CMS")
	if "Simulation" in cmsExtra:
		yLabelPos = 0.78	
	else:
		yLabelPos = 0.78	

	latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))				

	latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))				

	latexEta = ROOT.TLatex()
	latexEta.SetTextFont(42)
	latexEta.SetTextAlign(31)
	latexEta.SetTextSize(0.035)
	latexEta.SetNDC(True)		
	if obj == "Trk":
		latexEta.DrawLatex(0.62,0.7,"3rd Muon fired 2Mu1Tk trigger")
	else:	
		latexEta.DrawLatex(0.55,0.7,"3rd Muon fired 3Mu trigger")

	if data:
		c1.SaveAs("fitPlots/DsPhiMuNuFit_Data.pdf"%(label,obj))
	else:	
		c1.SaveAs("fitPlots/DsPhiMuNuFit_MC_%s_%s.pdf"%(label,obj))

	return ws.var("fsig").getVal(), ws.var("fsig").getError()
	




tree = ROOT.TChain()
tree.Add("AnalysedTree_data_control_2023_control_merged_2023Control.root/FinalTree")


ws = ROOT.RooWorkspace("w")
mass = ROOT.RooRealVar('mass','mass',1.9, 1.65, 2.1 )
getattr(ws,'import')(mass,ROOT.RooCmdArg())	
	
dataset = ROOT.RooDataSet('histRoo','histRoo',ROOT.RooArgSet(ws.var("mass")))



for ev in tree:
	tripletMass = ev.tripletMass
	if (tripletMass < 1.65 or tripletMass > 2.1): continue
	mass.setVal(tripletMass)
	dataset.add({mass})


getattr(ws,'import')(dataset, ROOT.RooCmdArg())


ws.factory("RooCBShape::cbDs(mass, meanDs[1.968,1.94,1.985], sigmaDs[0.01,0.005,0.05], alphaLDs[2,0.,5], nLDs[1.5,0.5,5])")
ws.factory("RooCBShape::cbD(mass, meanD[1.87,1.855,1.885], sigmaD[0.01,0.005,0.05], alphaLD[2,0.5,5], nLD[1.5,0.5,5])")
ws.factory("RooExponential::exp(mass, tau[-1.15, -2, -0.5])")

nD = ROOT.RooRealVar("nD","number of D meson events",2500,0.,15000)
nDs = ROOT.RooRealVar("nDs","number of Ds meson events",10000,0.,50000)
nBkg = ROOT.RooRealVar("nBkg","number of background events",100000,0.,1e6)

getattr(ws,'import')(nD, ROOT.RooCmdArg())
getattr(ws,'import')(nDs, ROOT.RooCmdArg())
getattr(ws,'import')(nBkg, ROOT.RooCmdArg())

ws.factory('SUM::model(nD*cbD, nDs*cbDs, nBkg*exp)')


c1 = ROOT.TCanvas("c1","c1",700,700)
c1.cd()	
plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)
style = setTDRStyle()
ROOT.gStyle.SetOptStat(0)
plotPad.UseCurrentStyle()
plotPad.Draw()	
plotPad.cd()
	
	
fitResult = ws.pdf("model").fitTo(ws.data("histRoo"), ROOT.RooFit.Save())

ws.var("mass").setBins(90)
frame = ws.var('mass').frame(ROOT.RooFit.Title('D_{s} candidate mass'))
frame.GetXaxis().SetTitle('m_{#mu#mu#pi} [GeV]')
frame.GetYaxis().SetTitle("Events / 5 MeV")
ROOT.RooAbsData.plotOn(ws.data('histRoo'), frame,ROOT.RooFit.Name("histRoo"))
ws.pdf('model').plotOn(frame,ROOT.RooFit.Name("model"))
# ~ ws.pdf('model').plotOn(frame,ROOT.RooFit.Components(ROOT.RooArgSet(ws.pdf("modelSig"))), ROOT.RooFit.Name("modelSig"),ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.LineStyle(ROOT.kDashed),Normalization=dict(scaleFactor=ws.var("nSig2"), scaleType=ROOT.RooAbsReal.Relative))
# ~ ws.pdf('model').plotOn(frame,ROOT.RooFit.Components(ROOT.RooArgSet(ws.pdf("exp"))), ROOT.RooFit.Name("model"),ROOT.RooFit.LineColor(ROOT.kGreen+2),ROOT.RooFit.LineStyle(ROOT.kDashed), Normalization=dict(scaleFactor=1.-ws.var("nSig2"), scaleType=ROOT.RooAbsReal.Relative))
ws.pdf('model').plotOn(frame,ROOT.RooFit.Components(ROOT.RooArgSet(ws.pdf("cbDs"))), ROOT.RooFit.Name("cbDs"),ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.LineStyle(ROOT.kDashed))
ws.pdf('model').plotOn(frame,ROOT.RooFit.Components(ROOT.RooArgSet(ws.pdf("exp"))), ROOT.RooFit.Name("model"),ROOT.RooFit.LineColor(ROOT.kGreen+2),ROOT.RooFit.LineStyle(ROOT.kDashed))
frame.Draw()


latex = ROOT.TLatex()
latex.SetTextFont(42)
latex.SetTextAlign(31)
latex.SetTextSize(0.04)
latex.SetNDC(True)
latexCMS = ROOT.TLatex()
latexCMS.SetTextFont(61)
latexCMS.SetTextSize(0.08)
latexCMS.SetNDC(True)
latexCMSExtra = ROOT.TLatex()
latexCMSExtra.SetTextFont(52)
latexCMSExtra.SetTextSize(0.045)
latexCMSExtra.SetNDC(True) 
	
latex.DrawLatex(0.95, 0.96, "(13.6 TeV)")

cmsExtra = "Preliminary"
latexCMS.DrawLatex(0.19,0.85,"CMS")
yLabelPos = 0.78	

latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))				

latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))				

latexEta = ROOT.TLatex()
latexEta.SetTextFont(42)
latexEta.SetTextAlign(31)
latexEta.SetTextSize(0.035)
latexEta.SetNDC(True)		

c1.SaveAs("DsPhiPiFit_Data.pdf")


