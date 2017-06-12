import sys
import time
import snap
import logging
import os

modefilename = "mode_table.bin"
crossnetfilename = "crossnet_table.bin"

graphobjfilename = "string-single-table-PNEANet.graph"

start = time.time()
context = snap.TTableContext()

# schema = snap.Schema()
# schema.Add(snap.TStrTAttrPr("SrcId", snap.atInt))
# schema.Add(snap.TStrTAttrPr("DstId", snap.atInt))
# schema.Add(snap.TStrTAttrPr("CrossNet", snap.atInt))
# schema.Add(snap.TStrTAttrPr("Id", snap.atInt))
# cross_table = snap.TTable.Load(schema, crossnetfilename, context, "\t", snap.TBool(False))

FIn = snap.TFIn(crossnetfilename)
cross_table = snap.TTable.Load(FIn, context)

end = time.time()

print "Loaded crossnet table. Time taken: ", end - start

start = time.time()
context = snap.TTableContext()

# schema = snap.Schema()
# schema.Add(snap.TStrTAttrPr("NodeId", snap.atInt))
# schema.Add(snap.TStrTAttrPr("Mode", snap.atInt))
# schema.Add(snap.TStrTAttrPr("Id", snap.atInt))
# mode_table = snap.TTable.Load(schema, modefilename, context, "\t", snap.TBool(False))

FIn = snap.TFIn(modefilename)
mode_table = snap.TTable.Load(FIn, context)
end = time.time()

print "Loaded mode table. Time taken: ", end - start

start = time.time()

edgeattrv = snap.TStr64V()
edgeattrv.Add("CrossNet")
edgeattrv.Add("Id")

nodeattrv = snap.TStr64V()
nodeattrv.Add("Mode")
nodeattrv.Add("Id")

# net will be an object of type snap.PNEANet
Graph = snap.ToNetwork(snap.PNEANet, cross_table, "SrcId", "DstId", edgeattrv, mode_table, "NodeId", nodeattrv, snap.aaFirst)

end = time.time()
print "Converted to PNEANet. Time: ", end - start


start = time.time()
outputPath = graphobjfilename
FOut = snap.TFOut(outputPath)
Graph.Save(FOut)
FOut.Flush()
end = time.time()
print "saving - ", end-start


print "\n loading graph:", graphobjfilename
FIn = snap.TFIn(graphobjfilename)
Graph = snap.TNEANet.Load(FIn)
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
