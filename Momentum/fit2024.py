import ROOT
from setTDRStyle import setTDRStyle
ROOT.gROOT.SetBatch(1)
import random

def fitAndPlot(ws, obj, label, data=False):


  c1 = ROOT.TCanvas("c1","c1",700,700)
  c1.cd()  
  plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)
  style = setTDRStyle()
  ROOT.gStyle.SetOptStat(0)
  plotPad.UseCurrentStyle()
  plotPad.Draw()  
  plotPad.cd()
  
  if False:
    firstFitResult = ws.pdf("modelTemp").fitTo(ws.data("histRoo"), ROOT.RooFit.Save(),ROOT.RooFit.Range(1.62,1.91))
    ws.var('sigmaDs').setVal(ws.var('sigmaD').getVal())
    ws.var('alphaLDs').setVal(ws.var('alphaLD').getVal())
    ws.var('nLDs').setVal(ws.var('nLD').getVal())
    ws.var('meanD').setConstant()
    ws.var('sigmaD').setConstant()
    ws.var('alphaLD').setConstant()
    ws.var('nLD').setConstant()

    ws.var("mass").setBins(90)
    frame = ws.var('mass').frame(ROOT.RooFit.Title('D_{s} candidate mass'))
    frame.GetXaxis().SetTitle('m_{#mu#mu#pi} [GeV]')
    frame.GetYaxis().SetTitle("Events / 5 MeV")
    ROOT.RooAbsData.plotOn(ws.data('histRoo'), frame,ROOT.RooFit.Name("histRoo"))
    ws.pdf('modelTemp').plotOn(frame,ROOT.RooFit.Name("model"))
    # ~ ws.pdf('model').plotOn(frame,ROOT.RooFit.Components(ROOT.RooArgSet(ws.pdf("modelSig"))), ROOT.RooFit.Name("modelSig"),ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.LineStyle(ROOT.kDashed),Normalization=dict(scaleFactor=ws.var("nSig2"), scaleType=ROOT.RooAbsReal.Relative))
    # ~ ws.pdf('model').plotOn(frame,ROOT.RooFit.Components(ROOT.RooArgSet(ws.pdf("exp"))), ROOT.RooFit.Name("model"),ROOT.RooFit.LineColor(ROOT.kGreen+2),ROOT.RooFit.LineStyle(ROOT.kDashed), Normalization=dict(scaleFactor=1.-ws.var("nSig2"), scaleType=ROOT.RooAbsReal.Relative))
    ws.pdf('model').plotOn(frame,ROOT.RooFit.Components(ROOT.RooArgSet(ws.pdf("cbD"))), ROOT.RooFit.Name("cbD"),ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.LineStyle(ROOT.kDashed))
    ws.pdf('model').plotOn(frame,ROOT.RooFit.Components(ROOT.RooArgSet(ws.pdf("exp"))), ROOT.RooFit.Name("exp"),ROOT.RooFit.LineColor(ROOT.kGreen+2),ROOT.RooFit.LineStyle(ROOT.kDashed))
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

    if data:
      c1.SaveAs("DsPhiPiFirstFit_Data_%s.pdf"%(label))
    else:  
      c1.SaveAs("DsPhiPiFirstFit_MC_%s.pdf"%(label))


  fitResult = ws.pdf("model").fitTo(ws.data("histRoo"), ROOT.RooFit.Save())

  ws.var("mass").setBins(90)
  frame = ws.var('mass').frame(ROOT.RooFit.Title('D_{s} candidate mass'))
  frame.GetXaxis().SetTitle('m_{#mu#mu#pi} [GeV]')
  frame.GetYaxis().SetTitle("Events / 5 MeV")
  ROOT.RooAbsData.plotOn(ws.data('histRoo'), frame,ROOT.RooFit.Name("histRoo"))
  ws.pdf('model').plotOn(frame,ROOT.RooFit.Name("model"))
  # ~ ws.pdf('model').plotOn(frame,ROOT.RooFit.Components(ROOT.RooArgSet(ws.pdf("modelSig"))), ROOT.RooFit.Name("modelSig"),ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.LineStyle(ROOT.kDashed),Normalization=dict(scaleFactor=ws.var("nSig2"), scaleType=ROOT.RooAbsReal.Relative))
  # ~ ws.pdf('model').plotOn(frame,ROOT.RooFit.Components(ROOT.RooArgSet(ws.pdf("exp"))), ROOT.RooFit.Name("model"),ROOT.RooFit.LineColor(ROOT.kGreen+2),ROOT.RooFit.LineStyle(ROOT.kDashed), Normalization=dict(scaleFactor=1.-ws.var("nSig2"), scaleType=ROOT.RooAbsReal.Relative))
  ws.pdf('model').plotOn(frame,ROOT.RooFit.Components(ROOT.RooArgSet(ws.pdf("modelSig"))), ROOT.RooFit.Name("modelSig"),ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.LineStyle(ROOT.kDashed))
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

  if data:
    c1.SaveAs("DsPhiPiFit_Data_%s.pdf"%(label))
  else:  
    c1.SaveAs("DsPhiPiFit_MC_%s.pdf"%(label))

  return ws.var("meanDs").getVal(), ws.var("meanDs").getError(), ws.var("sigmaDs").getVal(), ws.var("sigmaDs").getError()
  
  
def plotMassScale(era, results):
  
  
  graphData = ROOT.TGraphErrors()
  graphMC = ROOT.TGraphErrors()
  print ("Mass scale")
  weightedMeanData = 0
  weightSumData = 0
  weightedMeanMC = 0
  weightSumMC = 0
  for i in range(0, len(results)):
    print (results[i][2], results[i][3], results[i][4], results[i][5])
    weightedMeanData += results[i][2]*results[i][3]
    weightSumData += results[i][3]
    weightedMeanMC += results[i][4]*results[i][5]
    weightSumMC += results[i][5]
    graphData.SetPoint(i, results[i][0], results[i][2])
    graphData.SetPointError(i, results[i][1], results[i][3])
    graphMC.SetPoint(i, results[i][0], results[i][4])
    graphMC.SetPointError(i, results[i][1], results[i][5])
  
  print (weightedMeanData/weightSumData, weightedMeanMC/weightSumMC)
  
  graphData.SetMarkerColor(ROOT.kRed)
  graphData.SetLineColor(ROOT.kRed)
  graphData.SetMarkerStyle(20)
  graphMC.SetMarkerColor(ROOT.kBlue)
  graphMC.SetLineColor(ROOT.kBlue)
  graphMC.SetMarkerStyle(21)
  
  c1 = ROOT.TCanvas("c1","c1",700,700)
  c1.cd()  
  plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)
  style = setTDRStyle()
  ROOT.gStyle.SetOptStat(0)
  plotPad.UseCurrentStyle()
  plotPad.Draw()  
  plotPad.cd()

  plotPad.DrawFrame(0,1.945,2.5,1.99, ";|#eta| of most forward decay product; Reconstructed D_{s} mass [GeV]")

  graphData.Draw("samepe")
  graphMC.Draw("samepe")

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
    
    
  if era == "2022":  
    latex.DrawLatex(0.95, 0.96, "2022preEE (13.6 TeV)")
  elif era == "2022EE":  
    latex.DrawLatex(0.95, 0.96, "2022postEE (13.6 TeV)")
  if era == "2023":  
    latex.DrawLatex(0.95, 0.96, "2023preBPix (13.6 TeV)")
  if era == "2023BPix":  
    latex.DrawLatex(0.95, 0.96, "2023postBPix (13.6 TeV)")
  if era == "2022_Full":  
    latex.DrawLatex(0.95, 0.96, "1.7 fb^{-1} (13.6 TeV)")
  if era == "2023_Full":  
    latex.DrawLatex(0.95, 0.96, "1.4 fb^{-1} (13.6 TeV)")

  cmsExtra = "Preliminary"
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

  c1.SaveAs("massVsEta_%s.pdf"%(era))
  
  
def plotMassResolution(era, results):
  
  
  graph = ROOT.TGraphErrors()
  graph.SetPoint(0,0,0)
  graph.SetPointError(0,1,1)
  for i in range(0, len(results)):
    print (results[i][2]*1000, results[i][3]*1000, results[i][4]*1000, results[i][5]*1000, results[i][2]*1000/(results[i][4]*1000))
    graph.SetPoint(i+1, results[i][2]*1000, results[i][4]*1000)
    graph.SetPointError(i+1, results[i][3]*1000, results[i][5]*1000)
  
  graph.SetMarkerColor(ROOT.kBlack)
  graph.SetLineColor(ROOT.kBlack)
  graph.SetMarkerStyle(21)
  
  c1 = ROOT.TCanvas("c1","c1",700,700)
  c1.cd()  
  plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)
  style = setTDRStyle()
  ROOT.gStyle.SetOptStat(0)
  plotPad.UseCurrentStyle()
  plotPad.Draw()  
  plotPad.cd()

  plotPad.DrawFrame(0,0,25,25, ";Mass resolution in data [MeV]; Mass resolution in MC [GeV]")

  graph.Draw("samepe")
  
  f = ROOT.TF1('f1',"pol1",-1,30)
  graph.Fit('f1',"MR+")

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
    
  if era == "2022":  
    latex.DrawLatex(0.95, 0.96, "2022preEE (13.6 TeV)")
  elif era == "2022EE":  
    latex.DrawLatex(0.95, 0.96, "2022postEE (13.6 TeV)")
  if era == "2023":  
    latex.DrawLatex(0.95, 0.96, "2023preBPix (13.6 TeV)")
  if era == "2023BPix":  
    latex.DrawLatex(0.95, 0.96, "2023postBPix (13.6 TeV)")
  if era == "2022_Full":  
    latex.DrawLatex(0.95, 0.96, "1.7 fb^{-1} (13.6 TeV)")
  if era == "2023_Full":  
    latex.DrawLatex(0.95, 0.96, "1.4 fb^{-1} (13.6 TeV)")

  cmsExtra = "Preliminary"
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

  latexEta.DrawLatex(0.5,0.3,"#splitline{p0: %.3f #pm %.5f}{p1: %.3f #pm %.5f}"%(f.GetParameter(0), f.GetParError(0),f.GetParameter(1), f.GetParError(1)))        


  c1.SaveAs("massResDataVsMC_%s.pdf"%(era))
  


def runMass(ptBin, etaBin, era, data=True):


  tree = ROOT.TChain()
  if data:
    # ~ tree.Add("AnalysedTree_data_2022_tau3mu_merged_test8.root/FinalTree")
        if era == "2022":
            tree.Add("AnalysedTree_data_control_2022preEE_control_merged_2022Control.root/FinalTree")
        elif era == "2022EE":
            tree.Add("AnalysedTree_data_control_2022postEE_control_merged_2022Control.root/FinalTree")
        elif era == "2023":
            tree.Add("AnalysedTree_data_control_2023preBPix_control_merged_2023Control.root/FinalTree")
        elif era == "2022_Full":
            tree.Add("AnalysedTree_data_control_2022_control_merged_2022Control.root/FinalTree")
        elif era == "2023_Full":
            tree.Add("AnalysedTree_data_control_2023_control_merged_2023Control.root/FinalTree")
        elif era == '2024': 
            tree.Add("AnalysedTree_data_control_2024_control_merged_TEST.root/FinalTree")
        else:
            tree.Add("AnalysedTree_data_control_2023postBPix_control_merged_2023Control.root/FinalTree")

  else:  
    tree.Add("AnalysedTree_MC%s_DsPhiPi_tau3mu0.root/FinalTree"%era)

  # ~ hist = ROOT.TH1F('hist','hist',45, 1.65,2.1)
  if data:
    print(tree.GetEntries())
    
  ws = ROOT.RooWorkspace("w")
  mass = ROOT.RooRealVar('mass','mass',1.9, 1.65, 2.1 )
  getattr(ws,'import')(mass,ROOT.RooCmdArg())  
  
  dataset = ROOT.RooDataSet('histRoo','histRoo',ROOT.RooArgSet(ws.var("mass")))

  ptMin = ptBins[ptBin][0]
  ptMax = ptBins[ptBin][1]

  etaMin = etaBins[etaBin][0]
  etaMax = etaBins[etaBin][1]

  print (ptMin, ptMax, etaMin, etaMax)

  label = ptLabels[ptBin] + "_" + etaLabels[etaBin] + "_" + era
  for ev in tree:
    tripletMass = ev.tripletMass
    if ptBin == 0 and etaBin == 0 and not data and era == "2023_Full":
      tripletMass = ev.tripletMass*random.gauss(1,0.0024)
    if ptBin == 0 and etaBin in [3,4,5] and not data and era == "2024":
        tripletMass = ev.tripletMass*random.gauss(1,0.0025)
    if ptBin == 0 and etaBin == 6 and not data and era == "2024":
        tripletMass = ev.tripletMass*random.gauss(1,0.0055)
      
    highestEta = max(abs(ev.Etamu3), max(abs(ev.Etamu1), abs(ev.Etamu2)))
    if (ev.Ptmu3 < ptMin) or (ev.Ptmu3 > ptMax) or (highestEta < etaMin) or (highestEta > etaMax): continue
    if (tripletMass < 1.65 or tripletMass > 2.1): continue
    mass.setVal(tripletMass)
    dataset.add({mass})
    # ~ hist.Fill(ev.tripletMass)

  
    
  # ~ histRoo = ROOT.RooDataHist("histRoo","histRoo",ROOT.RooArgList(ws.var("mass")),hist)
  getattr(ws,'import')(dataset, ROOT.RooCmdArg())

  if data:

    ws.factory("RooCBShape::cbDs(mass, meanDs[1.968,1.94,1.985], sigmaDs[0.01,0.005,0.05], alphaLDs[2,0.,5], nLDs[1.5,0.5,5])")
    ws.factory("RooCBShape::cbD(mass, meanD[1.87,1.855,1.885], sigmaD[0.01,0.005,0.05], alphaLD[2,0.5,5], nLD[1.5,0.5,5])")
    ws.factory("RooExponential::exp(mass, tau[-1.15, -2, -0.5])")

    fsig = ROOT.RooRealVar("fsig","signal fraction",0.5,0.,1.)
    fsig2 = ROOT.RooRealVar("fsig2","signal2 fraction",0.5,0.,1.)
    fTemp = ROOT.RooRealVar("fTemp","temp fraction",0.5,0.,1.)

    # model(x) = fsig*sig(x) + (1-fsig)*bkg(x)
    modelSig = ROOT.RooAddPdf("modelSig","modelSig",ROOT.RooArgList(ws.pdf("cbDs"),ws.pdf("cbD")),ROOT.RooArgList(fsig2))
    getattr(ws,'import')(modelSig, ROOT.RooCmdArg())  
    model = ROOT.RooAddPdf("model","model",ROOT.RooArgList(ws.pdf("modelSig"),ws.pdf("exp")),ROOT.RooArgList(fsig))
    getattr(ws,'import')(model, ROOT.RooCmdArg())
    modelTemp = ROOT.RooAddPdf("modelTemp","modelTemp",ROOT.RooArgList(ws.pdf("cbD"),ws.pdf("exp")),ROOT.RooArgList(fTemp))
    getattr(ws,'import')(modelTemp, ROOT.RooCmdArg())
  else:
    ws.factory("RooCBShape::modelSig(mass, meanDs[1.9,1.8,2.1], sigmaDs[0.012,0.005,0.05], alphaLDs[2,0,50], nLDs[3,0,50])")
    ws.factory("RooExponential::exp(mass, tau[1.0, -10, 10])")

    fsig = ROOT.RooRealVar("fsig","signal fraction",0.5,0.,1.)

    # model(x) = fsig*sig(x) + (1-fsig)*bkg(x)
    model = ROOT.RooAddPdf("model","model",ROOT.RooArgList(ws.pdf("modelSig"),ws.pdf("exp")),ROOT.RooArgList(fsig))
    getattr(ws,'import')(model, ROOT.RooCmdArg())

  mass, massErr, sigma, sigmaErr = fitAndPlot(ws, "DsMass", label=label, data=data)

  print (mass, sigma)


  return label, mass, massErr,  sigma, sigmaErr



ptBins = [[0,1000], [0,4],[4,1000],[3.5,1000]]
#etaBins = [[0,0.6],[0.6,1.2],[1.2,2.4]]
etaBins = [[0,0.3],[0.3,0.6],[0.6,0.9],[0.9,1.2],[1.2,1.5],[1.5,1.8],[1.8,2.4]]
ptLabels = ["ptInclusive", "pt0to4", 'pt4toInf','pt3p5toInf']
#etaLabels = ["eta0to0p6", 'eta0p6to1p2','eta1p2to2p4']
etaLabels = ["eta0to0p3", 'eta0p3to0p6', 'eta0p6to0p9','eta0p9to1p2','eta1p2to1p5', 'eta1p5to1p8', 'eta1p8to2p4']
# ~ eras = ["2022_Full","2022", "2022EE", "2023_Full", "2023", "2023BPix"]
#eras = ["2022_Full", "2023_Full", '2024']
eras = ['2024']
# ~ eras = ["2023_Full"]

resultsMass = {}
resultsSigma = {}

for era in eras:
  # ~ for i in range(0, len(ptBins)):
  resultsMass[era] = []
  resultsSigma[era] = []
  for i in range(0, 1):
    for j in range(0,len(etaBins)):
      etaMin = etaBins[j][0]
      etaMax = etaBins[j][1]
      etaMean = etaMin + (etaMax - etaMin)/2
      etaErr = (etaMax - etaMin)/2
      label , massMC, massErrMC, sigmaMC, sigmaErrMC =  runMass(i,j,era=era, data=False)
      label , mass, massErr, sigma, sigmaErr = runMass(i,j,era=era,data=True)

      #print(etaBins[j], 100*(massMC-mass)/mass)
      #print(etaBins[j], 100*(sigmaMC-sigma)/sigma)
      print(etaBins[j], sigma, sigmaMC)
      resultsMass[era].append([etaMean, etaErr, mass, massErr, massMC, massErrMC])
      resultsSigma[era].append([etaMean, etaErr, sigma, sigmaErr, sigmaMC, sigmaErrMC])
      
      
  plotMassScale(era, resultsMass[era])
  plotMassResolution(era, resultsSigma[era])


print (resultsMass)
print (resultsSigma)


avgData = 0
wgtData = 0
avgMC = 0
wgtMC = 0
for i in range(0, len(resultsMass['2022_Full'])):
  print (resultsMass['2022_Full'][i][2], resultsMass['2022_Full'][i][4], resultsMass['2022_Full'][i][2]/resultsMass['2022_Full'][i][4])
  avgData += resultsMass['2022_Full'][i][2]*resultsMass['2022_Full'][i][3]
  wgtData += resultsMass['2022_Full'][i][3]
  avgMC += resultsMass['2022_Full'][i][4]*resultsMass['2022_Full'][i][5]
  wgtMC += resultsMass['2022_Full'][i][5]
print (1.- avgData/wgtData/(avgMC/wgtMC))
for i in range(0, len(resultsMass['2023_Full'])):
  print (resultsMass['2022_Full'][i][2], resultsMass['2022_Full'][i][4], resultsMass['2023_Full'][i][2]/resultsMass['2023_Full'][i][4])
  avgData += resultsMass['2023_Full'][i][2]*resultsMass['2023_Full'][i][3]
  wgtData += resultsMass['2023_Full'][i][3]
  avgMC += resultsMass['2023_Full'][i][4]*resultsMass['2023_Full'][i][5]
  wgtMC += resultsMass['2023_Full'][i][5]
print (1.- avgData/wgtData/(avgMC/wgtMC))
# ~ graphData2022 = ROOT.TGraphErrors()
# ~ graphMC2022 = ROOT.TGraphErrors()
# ~ graphData2022EE = ROOT.TGraphErrors()
# ~ graphMC2022EE = ROOT.TGraphErrors()
# ~ graphData2023 = ROOT.TGraphErrors()
# ~ graphMC2023 = ROOT.TGraphErrors()
# ~ graphData2023BPix = ROOT.TGraphErrors()
# ~ graphMC2023BPix = ROOT.TGraphErrors()

# ~ for i in range(0, len(resultsMass['2022'])):
  # ~ graphData2022.SetPoint(i, resultsMass['2022'][i][0], resultsMass['2022'][i][2])
  # ~ graphData2022.SetPointError(i, resultsMass['2022'][i][1], resultsMass['2022'][i][3])
  # ~ graphMC2022.SetPoint(i, resultsMass['2022'][i][0], resultsMass['2022'][i][4])
  # ~ graphMC2022.SetPointError(i, resultsMass['2022'][i][1], resultsMass['2022'][i][5])

# ~ for i in range(0, len(resultsMass['2022EE'])):
  # ~ graphData2022EE.SetPoint(i, resultsMass['2022EE'][i][0], resultsMass['2022EE'][i][2])
  # ~ graphData2022EE.SetPointError(i, resultsMass['2022EE'][i][1], resultsMass['2022EE'][i][3])
  # ~ graphMC2022EE.SetPoint(i, resultsMass['2022EE'][i][0], resultsMass['2022EE'][i][4])
  # ~ graphMC2022EE.SetPointError(i, resultsMass['2022EE'][i][1], resultsMass['2022EE'][i][5])

# ~ for i in range(0, len(resultsMass['2023'])):
  # ~ graphData2023.SetPoint(i, resultsMass['2023'][i][0], resultsMass['2023'][i][2])
  # ~ graphData2023.SetPointError(i, resultsMass['2023'][i][1], resultsMass['2023'][i][3])
  # ~ graphMC2023.SetPoint(i, resultsMass['2023'][i][0], resultsMass['2023'][i][4])
  # ~ graphMC2023.SetPointError(i, resultsMass['2023'][i][1], resultsMass['2023'][i][5])

# ~ for i in range(0, len(resultsMass['2023BPix'])):
  # ~ graphData2023BPix.SetPoint(i, resultsMass['2023BPix'][i][0], resultsMass['2023BPix'][i][2])
  # ~ graphData2023BPix.SetPointError(i, resultsMass['2023BPix'][i][1], resultsMass['2023BPix'][i][3])
  # ~ graphMC2023BPix.SetPoint(i, resultsMass['2023BPix'][i][0], resultsMass['2023BPix'][i][4])
  # ~ graphMC2023BPix.SetPointError(i, resultsMass['2023BPix'][i][1], resultsMass['2023BPix'][i][5])


# ~ graphData2022.SetMarkerColor(ROOT.TColor.GetColor("#5790fc"))
# ~ graphData2022.SetLineColor(ROOT.TColor.GetColor("#5790fc"))
# ~ graphMC2022.SetMarkerColor(ROOT.TColor.GetColor("#5790fc"))
# ~ graphMC2022.SetLineColor(ROOT.TColor.GetColor("#5790fc"))
# ~ graphMC2022.SetLineStyle(ROOT.kDashed)
# ~ graphMC2022.SetMarkerStyle(21)
# ~ graphData2022EE.SetMarkerColor(ROOT.TColor.GetColor("#f89c20"))
# ~ graphData2022EE.SetLineColor(ROOT.TColor.GetColor("#f89c20"))
# ~ graphMC2022EE.SetMarkerColor(ROOT.TColor.GetColor("#f89c20"))
# ~ graphMC2022EE.SetLineColor(ROOT.TColor.GetColor("#f89c20"))
# ~ graphMC2022EE.SetLineStyle(ROOT.kDashed)
# ~ graphMC2022EE.SetMarkerStyle(21)
# ~ graphData2023.SetMarkerColor(ROOT.TColor.GetColor("#e42536"))
# ~ graphData2023.SetLineColor(ROOT.TColor.GetColor("#e42536"))
# ~ graphMC2023.SetMarkerColor(ROOT.TColor.GetColor("#e42536"))
# ~ graphMC2023.SetLineColor(ROOT.TColor.GetColor("#e42536"))
# ~ graphMC2023.SetLineStyle(ROOT.kDashed)
# ~ graphMC2023.SetMarkerStyle(21)
# ~ graphData2023BPix.SetMarkerColor(ROOT.TColor.GetColor("#964a8b"))
# ~ graphData2023BPix.SetLineColor(ROOT.TColor.GetColor("#964a8b"))
# ~ graphMC2023BPix.SetMarkerColor(ROOT.TColor.GetColor("#964a8b"))
# ~ graphMC2023BPix.SetLineColor(ROOT.TColor.GetColor("#964a8b"))
# ~ graphMC2023BPix.SetLineStyle(ROOT.kDashed)
# ~ graphMC2023BPix.SetMarkerStyle(21)


# ~ c1 = ROOT.TCanvas("c1","c1",700,700)
# ~ c1.cd()  
# ~ plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)
# ~ style = setTDRStyle()
# ~ ROOT.gStyle.SetOptStat(0)
# ~ plotPad.UseCurrentStyle()
# ~ plotPad.Draw()  
# ~ plotPad.cd()

# ~ plotPad.DrawFrame(0,1.945,2.5,1.99, ";|#eta| of most forward decay product; Reconstructed D_{s} mass [GeV]")

# ~ graphData2022.Draw("samepe")
# ~ graphMC2022.Draw("samepe")
# ~ graphData2022EE.Draw("samepe")
# ~ graphMC2022EE.Draw("samepe")
# ~ graphData2023.Draw("samepe")
# ~ graphMC2023.Draw("samepe")
# ~ graphData2023BPix.Draw("samepe")
# ~ graphMC2023BPix.Draw("samepe")

# ~ latex = ROOT.TLatex()
# ~ latex.SetTextFont(42)
# ~ latex.SetTextAlign(31)
# ~ latex.SetTextSize(0.04)
# ~ latex.SetNDC(True)
# ~ latexCMS = ROOT.TLatex()
# ~ latexCMS.SetTextFont(61)
# ~ latexCMS.SetTextSize(0.08)
# ~ latexCMS.SetNDC(True)
# ~ latexCMSExtra = ROOT.TLatex()
# ~ latexCMSExtra.SetTextFont(52)
# ~ latexCMSExtra.SetTextSize(0.045)
# ~ latexCMSExtra.SetNDC(True) 
  
# ~ latex.DrawLatex(0.95, 0.96, "(13.6 TeV)")

# ~ cmsExtra = "Preliminary"
# ~ latexCMS.DrawLatex(0.19,0.85,"CMS")
# ~ if "Simulation" in cmsExtra:
  # ~ yLabelPos = 0.78  
# ~ else:
  # ~ yLabelPos = 0.78  

# ~ latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))        

# ~ latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))        

# ~ latexEta = ROOT.TLatex()
# ~ latexEta.SetTextFont(42)
# ~ latexEta.SetTextAlign(31)
# ~ latexEta.SetTextSize(0.035)
# ~ latexEta.SetNDC(True)    

# ~ c1.SaveAs("massVsEta_Summary.pdf")
  


# ~ graphData2022 = ROOT.TGraphErrors()
# ~ graphMC2022 = ROOT.TGraphErrors()
# ~ graphData2022EE = ROOT.TGraphErrors()
# ~ graphMC2022EE = ROOT.TGraphErrors()
# ~ graphData2023 = ROOT.TGraphErrors()
# ~ graphMC2023 = ROOT.TGraphErrors()
# ~ graphData2023BPix = ROOT.TGraphErrors()
# ~ graphMC2023BPix = ROOT.TGraphErrors()

# ~ for i in range(0, len(resultsSigma['2022'])):
  # ~ graphData2022.SetPoint(i, resultsSigma['2022'][i][0], resultsSigma['2022'][i][2]*1000)
  # ~ graphData2022.SetPointError(i, resultsSigma['2022'][i][1], resultsSigma['2022'][i][3]*1000)
  # ~ graphMC2022.SetPoint(i, resultsSigma['2022'][i][0], resultsSigma['2022'][i][4]*1000)
  # ~ graphMC2022.SetPointError(i, resultsSigma['2022'][i][1], resultsSigma['2022'][i][5]*1000)

# ~ for i in range(0, len(resultsSigma['2022EE'])):
  # ~ graphData2022EE.SetPoint(i, resultsSigma['2022EE'][i][0], resultsSigma['2022EE'][i][2]*1000)
  # ~ graphData2022EE.SetPointError(i, resultsSigma['2022EE'][i][1], resultsSigma['2022EE'][i][3]*1000)
  # ~ graphMC2022EE.SetPoint(i, resultsSigma['2022EE'][i][0], resultsSigma['2022EE'][i][4]*1000)
  # ~ graphMC2022EE.SetPointError(i, resultsSigma['2022EE'][i][1], resultsSigma['2022EE'][i][5]*1000)

# ~ for i in range(0, len(resultsSigma['2023'])):
  # ~ graphData2023.SetPoint(i, resultsSigma['2023'][i][0], resultsSigma['2023'][i][2]*1000)
  # ~ graphData2023.SetPointError(i, resultsSigma['2023'][i][1], resultsSigma['2023'][i][3]*1000)
  # ~ graphMC2023.SetPoint(i, resultsSigma['2023'][i][0], resultsSigma['2023'][i][4]*1000)
  # ~ graphMC2023.SetPointError(i, resultsSigma['2023'][i][1], resultsSigma['2023'][i][5]*1000)

# ~ for i in range(0, len(resultsSigma['2023BPix'])):
  # ~ graphData2023BPix.SetPoint(i, resultsSigma['2023BPix'][i][0], resultsSigma['2023BPix'][i][2]*1000)
  # ~ graphData2023BPix.SetPointError(i, resultsSigma['2023BPix'][i][1], resultsSigma['2023BPix'][i][3]*1000)
  # ~ graphMC2023BPix.SetPoint(i, resultsSigma['2023BPix'][i][0], resultsSigma['2023BPix'][i][4]*1000)
  # ~ graphMC2023BPix.SetPointError(i, resultsSigma['2023BPix'][i][1], resultsSigma['2023BPix'][i][5]*1000)


# ~ graphData2022.SetMarkerColor(ROOT.TColor.GetColor("#5790fc"))
# ~ graphData2022.SetLineColor(ROOT.TColor.GetColor("#5790fc"))
# ~ graphMC2022.SetMarkerColor(ROOT.TColor.GetColor("#5790fc"))
# ~ graphMC2022.SetLineColor(ROOT.TColor.GetColor("#5790fc"))
# ~ graphMC2022.SetLineStyle(ROOT.kDashed)
# ~ graphMC2022.SetMarkerStyle(21)
# ~ graphData2022EE.SetMarkerColor(ROOT.TColor.GetColor("#f89c20"))
# ~ graphData2022EE.SetLineColor(ROOT.TColor.GetColor("#f89c20"))
# ~ graphMC2022EE.SetMarkerColor(ROOT.TColor.GetColor("#f89c20"))
# ~ graphMC2022EE.SetLineColor(ROOT.TColor.GetColor("#f89c20"))
# ~ graphMC2022EE.SetLineStyle(ROOT.kDashed)
# ~ graphMC2022EE.SetMarkerStyle(21)
# ~ graphData2023.SetMarkerColor(ROOT.TColor.GetColor("#e42536"))
# ~ graphData2023.SetLineColor(ROOT.TColor.GetColor("#e42536"))
# ~ graphMC2023.SetMarkerColor(ROOT.TColor.GetColor("#e42536"))
# ~ graphMC2023.SetLineColor(ROOT.TColor.GetColor("#e42536"))
# ~ graphMC2023.SetLineStyle(ROOT.kDashed)
# ~ graphMC2023.SetMarkerStyle(21)
# ~ graphData2023BPix.SetMarkerColor(ROOT.TColor.GetColor("#964a8b"))
# ~ graphData2023BPix.SetLineColor(ROOT.TColor.GetColor("#964a8b"))
# ~ graphMC2023BPix.SetMarkerColor(ROOT.TColor.GetColor("#964a8b"))
# ~ graphMC2023BPix.SetLineColor(ROOT.TColor.GetColor("#964a8b"))
# ~ graphMC2023BPix.SetLineStyle(ROOT.kDashed)
# ~ graphMC2023BPix.SetMarkerStyle(21)



# ~ plotPad.DrawFrame(0,0,2.5,25, ";|#eta| of most forward decay product; Mass resolution [MeV]")


# ~ graphData2022.Draw("samepe")
# ~ graphMC2022.Draw("samepe")
# ~ graphData2022EE.Draw("samepe")
# ~ graphMC2022EE.Draw("samepe")
# ~ graphData2023.Draw("samepe")
# ~ graphMC2023.Draw("samepe")
# ~ graphData2023BPix.Draw("samepe")
# ~ graphMC2023BPix.Draw("samepe")


# ~ latex = ROOT.TLatex()
# ~ latex.SetTextFont(42)
# ~ latex.SetTextAlign(31)
# ~ latex.SetTextSize(0.04)
# ~ latex.SetNDC(True)
# ~ latexCMS = ROOT.TLatex()
# ~ latexCMS.SetTextFont(61)
# ~ latexCMS.SetTextSize(0.08)
# ~ latexCMS.SetNDC(True)
# ~ latexCMSExtra = ROOT.TLatex()
# ~ latexCMSExtra.SetTextFont(52)
# ~ latexCMSExtra.SetTextSize(0.045)
# ~ latexCMSExtra.SetNDC(True) 
  
# ~ latex.DrawLatex(0.95, 0.96, "(13.6 TeV)")

# ~ cmsExtra = "Preliminary"
# ~ latexCMS.DrawLatex(0.19,0.85,"CMS")
# ~ if "Simulation" in cmsExtra:
  # ~ yLabelPos = 0.78  
# ~ else:
  # ~ yLabelPos = 0.78  

# ~ latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))        

# ~ latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))        

# ~ latexEta = ROOT.TLatex()
# ~ latexEta.SetTextFont(42)
# ~ latexEta.SetTextAlign(31)
# ~ latexEta.SetTextSize(0.035)
# ~ latexEta.SetNDC(True)    



# ~ c1.SaveAs("massResDataVsMC_Summary.pdf")
