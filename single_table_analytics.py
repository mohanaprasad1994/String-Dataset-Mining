import sys
import time
import snap
import logging
import os

graphfilename = "edges-directed.tsv"
graphobjfilename = "string-single-table-PN.graph"

start = time.time()
schema = snap.Schema()
context = snap.TTableContext()
schema.Add(snap.TStrTAttrPr("srcID", snap.atInt))
schema.Add(snap.TStrTAttrPr("dstID", snap.atInt))
table = snap.TTable.LoadSS(schema, graphfilename, context, "\t", snap.TBool(False))
end = time.time()

print "Loaded edge table. Time taken: ", end - start

# graph will be an object of type snap.PNGraph
start = time.time()
Graph = snap.ToGraph(snap.PNGraph, table, "srcID", "dstID", snap.aaFirst)
end = time.time()
print "Converted to PNGraph. Time: ", end - start


start = time.time()
outputPath = graphobjfilename
FOut = snap.TFOut(outputPath)
Graph.Save(FOut)
FOut.Flush()
end = time.time()
print "saving - ", end-start


print "\n loading graph:", graphobjfilename
FIn = snap.TFIn(graphobjfilename)
Graph = snap.TNGraph.Load(FIn)
end = time.time()
print "time for loading PNgraph ", end-start


print "Running PrintInfo"
start_time = time.time()
snap.PrintInfo(Graph, "Python type PNGraph")
end_time = time.time()
print "PrintInfo() takes %s seconds" % (end_time - start_time)

start = time.time()
ClustCoeff = snap.GetClustCf (Graph, -1)
end = time.time()
print "clustering coeff of entire graph without sampling: ", ClustCoeff, " time taken: ", end-start

start = time.time()
DegToCntV = snap.TIntPr64V()
snap.GetDegCnt(Graph, DegToCntV)
end = time.time()
print "Degree histogram (GetDegCnt) of entire network. Time: ", end - start
st = ""
for item in DegToCntV:
    st += "%d nodes with degree %d\n" % (item.GetVal2(), item.GetVal1())
with open("deg_hist_PNGraph.tsv", 'w') as degfile:
    degfile.write(st)

start = time.time()
UGraph = snap.ConvertGraph(snap.PUNGraph, Graph)
end = time.time()
print "converted to PUNGraph. Time: ", end-start
snap.PrintInfo(UGraph, "Python type PUNGraph")

start = time.time()
MxWcc = snap.GetMxWcc(Graph)
end = time.time()
print "time for GetMxWcc ", end - start
st = ""
for EI in MxWcc.Edges():
    st += "edge: (%d, %d)\n" % (EI.GetSrcNId(), EI.GetDstNId())
with open("wcc_largest_PNgraph.tsv", 'w') as wccfile:
    wccfile.write(st)

start = time.time()
dia = snap.GetBfsEffDiam(MxWcc, 10)
end = time.time()
print "diameter of largest WCC ",dia," time taken ", end-start
