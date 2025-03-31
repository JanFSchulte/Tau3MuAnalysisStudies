import ROOT
from setTDRStyle import setTDRStyle


def fitAndPlot(ws, obj, label, data=False):
	
	fitResult = ws.pdf("model").fitTo(ws.data("hist%sRoo"%obj), ROOT.RooFit.Save())


	c1 = ROOT.TCanvas("cfrom scipy.stats import binomtest1","c1",700,700)
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
		c1.SaveAs("fitPlots/DsPhiMuNuFit_Data_%s_%s.pdf"%(label,obj))
	else:	
		c1.SaveAs("fitPlots/DsPhiMuNuFit_MC_%s_%s.pdf"%(label,obj))

	return ws.var("fsig").getVal(), ws.var("fsig").getError()
	


def runEff(ptBin, etaBin, era, data=True):


	tree = ROOT.TChain()
	if data:
		if "2022" in era:
			tree.Add("AnalysedTree_data_2022_tau3mu_merged_test8.root/FinalTree")
		else:
			tree.Add("AnalysedTree_data_2023_tau3mu_merged_2023v1.root/FinalTree")
	else:	
		tree.Add("AnalysedTree_MC_DsPhiMuNu_tau3mu_%s.root/FinalTree"%era)

	histTrk = ROOT.TH1F('trkHist','trkHist',40, 0.8,1.2)
	histMu = ROOT.TH1F('muHist','muHist',40, 0.8,1.2)

	ptMin = ptBins[ptBin][0]
	ptMax = ptBins[ptBin][1]

	etaMin = etaBins[etaBin][0]
	etaMax = etaBins[etaBin][1]

	print (ptMin, ptMax, etaMin, etaMax)

	label = ptLabels[ptBin] + "_" + etaLabels[etaBin] + "_" + era
	for ev in tree:
		if (ev.Ptmu3 < ptMin) or (ev.Ptmu3 > ptMax) or (abs(ev.Etamu3) < etaMin) or (abs(ev.Etamu3) > etaMax): continue
		if ev.mu3Matched2Mu1Tk > 0:
			histTrk.Fill(ev.phi_mass)
		if ev.mu3Matched3Mu > 0 and ev.mu3Matched2Mu1Tk > 0:
			histMu.Fill(ev.phi_mass)

	numTk = histTrk.GetEntries()
	numMu = histMu.GetEntries()

	ws = ROOT.RooWorkspace("w")
	mass = ROOT.RooRealVar('mass','mass',1.0, 0.8, 1.2 )
	getattr(ws,'import')(mass,ROOT.RooCmdArg())			
	histTrkRoo = ROOT.RooDataHist("histTrkRoo","histTrkRoo",ROOT.RooArgList(ws.var("mass")),histTrk)
	getattr(ws,'import')(histTrkRoo, ROOT.RooCmdArg())
	histMuRoo = ROOT.RooDataHist("histMuRoo","histMuRoo",ROOT.RooArgList(ws.var("mass")),histMu)
	getattr(ws,'import')(histMuRoo, ROOT.RooCmdArg())

	ws.factory("RooCBShape::cb(mass, mean[1.0,-0.8,1.2], sigma[0.01,0.005,0.2], alphaL[2,0,25], nL[3,0,25])")
	ws.factory("RooExponential::exp(mass, tau[1.0, -10, 10])")

	fsig = ROOT.RooRealVar("fsig","signal fraction",0.5,0.,1.)

	# model(x) = fsig*sig(x) + (1-fsig)*bkg(x)
	model = ROOT.RooAddPdf("model","model",ROOT.RooArgList(ws.pdf("cb"),ws.pdf("exp")),ROOT.RooArgList(fsig))
	getattr(ws,'import')(model, ROOT.RooCmdArg())

	fSigTk, fSigErrTk = fitAndPlot(ws, "Trk", label=label, data=data)
	fSigMu, fSigErrMu = fitAndPlot(ws, "Mu", label=label, data=data)

	print (fSigErrTk, fSigErrMu)

	eff = (numMu * fSigMu) / (numTk * fSigTk)
	eff2 = (numMu) / (numTk)
	lower_error = eff2 - ROOT.TEfficiency.ClopperPearson(numTk, numMu,  0.683,  False)
	upper_error = ROOT.TEfficiency.ClopperPearson(numTk, numMu,  0.683,  True) - eff2
	
	fitErr = max(fSigErrTk, fSigErrMu)
	lower_error = (lower_error**2 + fitErr**2)**0.5
	upper_error = (upper_error**2 + fitErr**2)**0.5
	
	if ((eff + upper_error) > 1.0): 
		upper_error = 1 - eff

	print ("eff %s = %f + %s - %f"%(label, eff, upper_error, lower_error))
	return label, eff, upper_error, lower_error



ptBins = [[0,1000], [0,4],[4,1000],[3.5,1000]]
etaBins = [[0,2.4],[0,1.2],[1.2,2.4]]
ptLabels = ["ptInclusive", "pt0to4", 'pt4toInf','pt3p5toInf']
etaLabels = ["etaInclusive", 'eta0to1p2','eta1p2to2p4']
# ~ eras = ["2022", "2022EE", "2023", "2023BPix"]
eras = ["2022_Full", "2023_Full"]

results = []

for era in eras:
	for i in range(0, len(ptBins)):
		for j in range(0,len(etaBins)):
			label , eff, upper_error, lower_error =  runEff(i,j,era=era, data=False)
			results.append(["MC", era, label, eff, upper_error, lower_error])
			label , eff, upper_error, lower_error = runEff(i,j,era=era,data=True)
			results.append(["Data", era, label, eff, upper_error, lower_error])



for result in results:
	print (result[0], result[1], result[2], result[3], result[4], result[5])
