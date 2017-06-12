'''
Script to print basic statistics of the Baylor dataset.

Usage:
python baylor_get_stats.py <input_file>

Positional Arguments:
input_file : Path to the multi-modal network

Example Usage:
Input file : baylor.graph

Command line:
python baylor_get_stats.py baylor.graph
'''

import sys
sys.path.insert(0, './../../swig/')
import snap
import argparse
from collections import defaultdict
import time

parser = argparse.ArgumentParser(description='Print basic statistics of the Genemania dataset')
parser.add_argument('files', nargs='+', help='path to the multi-modal network')

args = parser.parse_args()



for f in args.files:
	
	start = time.time()
    print "\n Processing graph:", f
    FIn = snap.TFIn(f)
    Graph = snap.TMMNet.Load(FIn)
    end = time.time()
    print "time for loading modal graph ", end-start
    ct = 0
    tot = 0
    print "Writing %d Modes"
    modeneti = Graph.BegModeNetI()
    modestring = ""
    while modeneti < Graph.EndModeNetI():
        name = Graph.GetModeName(modeneti.GetModeId())
        modeNet = modeneti.GetModeNet()
        ct += 1
        tot += modeNet.GetNodes()
        modestring += '%s\t%s\n' % (name, modeNet.GetNodes())
        modeneti.Next()
    with open("string_modes_complete.tsv", 'w') as modefile:
        modefile.write(modestring)
    print '%d total Modes' % Graph.GetModeNets()
    print "Modes ",ct," total nodes ", tot," avg num nodes ", 1.0*tot/ct

    ct = 0
    tot = 0
    print "Printing CrossNets"
    crossnetids = snap.TInt64V()
    crossneti = Graph.BegCrossNetI()
    crossnetnames = snap.TStr64V()
    crossnetstring = ""
    while crossneti < Graph.EndCrossNetI():
        crossnetids.Add(crossneti.GetCrossId())
        name = Graph.GetCrossName(crossneti.GetCrossId())
        crossnet = crossneti.GetCrossNet()
        crossnetnames.Add(name)
        ct += 1
        tot += crossnet.GetEdges()
        crossnetstring += '%s\t%s\n' % (name, crossnet.GetEdges())
        crossneti.Next()
    with open("string_crossnets_complete.tsv", 'w') as crossnetfile:
        crossnetfile.write(crossnetstring)
    print '%d total Crossnets' % Graph.GetCrossNets()
    print "crossnets ",ct, "total edges ", tot, "avg edges ",1.0*tot/ct

    # Convert to TNEANet

    # These are mappings consisting of triples of (modeid, old attribute name, new attribute name)
    nodeattrmapping = snap.TIntStrStrTr64V()
    edgeattrmapping = snap.TIntStrStrTr64V()

    start_time = time.time()
    DirectedNetwork = Graph.ToNetwork(crossnetids, nodeattrmapping, edgeattrmapping)
    #DirectedNetwork = Graph.ToNetworkMP(crossnetnames)
    end_time = time.time()
    print "Converting to TNEANet  takes %s seconds" % (end_time - start_time)

    print "Running PrintInfo"
    start_time = time.time()
    snap.PrintInfo(DirectedNetwork, "Python type PNEANet")
    end_time = time.time()
    print "PrintInfo() takes %s seconds" % (end_time - start_time)

    start = time.time()
    ClustCoeff = snap.GetClustCf (DirectedNetwork, -1)
    end = time.time()
    print "clustering coeff of entire graph without sampling: ", ClustCoeff, " time taken: ", end-start

    start = time.time()
    DegToCntV = snap.TIntPr64V()
    snap.GetDegCnt(DirectedNetwork, DegToCntV)
    end = time.time()
    print "Degree histogram (GetDegCnt) of entire network. Time: ", end - start
    st = ""
    for item in DegToCntV:
        st += "%d nodes with degree %d\n" % (item.GetVal2(), item.GetVal1())
    with open("deg_hist.tsv", 'w') as degfile:
        degfile.write(st)

    start = time.time()
    UGraph = snap.ConvertGraph(snap.PUNGraph, DirectedNetwork)
    end = time.time()
    print "converted to PUNGraph. Time: ", end-start
    snap.PrintInfo(UGraph, "Python type PUNGraph")

    start = time.time()
    MxWcc = snap.GetMxWcc(DirectedNetwork)
    end = time.time()
    print "time for GetMxWcc ", end - start
    st = ""
    for EI in MxWcc.Edges():
        st += "edge: (%d, %d)\n" % (EI.GetSrcNId(), EI.GetDstNId())
    with open("wcc_largest.tsv", 'w') as wccfile:
        wccfile.write(st)

    start = time.time()
    dia = snap.GetBfsEffDiam(MxWcc, 10)
    end = time.time()
    print "diameter of largest WCC ", dia ," time : ", end-start

    # CntV = snap.TIntPr64V()
    # snap.GetWccSzCnt(DirectedNetwork, CntV)
    # sizestring = ""
    # for p in CntV:
    #     sizestring += "%d\t%d\n" % (p.GetVal1(), p.GetVal2())
    # with open("wcc_complete.tsv", 'w') as wccfile:
    #     wccfile.write(sizestring)
    # print "diameter %d" % snap.GetBfsFullDiam(DirectedNetwork, 10)

    #UGraph = snap.ConvertGraph(snap.PUNGraph, DirectedNetwork)
    #snap.PrintInfo(UGraph, "Python type PUNGraph")