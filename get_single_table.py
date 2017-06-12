### File to read all the tables (modes and crossnets) and generate a single table
import sys
import time
sys.path.insert(0, './../../swig/')
import snap
import argparse
import logging
import os


NodeMap = {}
node_ct = 0

start = time.time()
mode_dir = 'output/modes'
ct = 0
num_nodes = 0
nodes_fil = open("nodes.tsv", 'w')
# Loading Modes (Gene)
for f in os.listdir('output/modes'):
    splitName = f.split('-')
    if len(splitName) == 3:
        NodeMap[splitName[1]] = {}
        ct += 1
        fil = open(mode_dir + '/' + f,'r')
        fil.readline()
        fil.readline()
        fil.readline()

        for line in fil:
            NodeMap[splitName[1]][line.split()[0]] = node_ct
            nodes_fil.write(str(node_ct)+"\n")
            node_ct += 1
            num_nodes += 1

nodes_fil.close()
end = time.time()
print "modes - ",ct, ",  ",num_nodes," nodes, time: ", end-start

start = time.time()
ct = 0
cross_fil1 = open("edges.tsv", 'w')
cross_fil = open("edges-directed.tsv", 'w')
num_edges = 0
# Loading Cross-Nets
cog_cross_dir = 'output/cog_crossnet/'
for f in os.listdir('output/cog_crossnet'):
    splitName = f.split('-')
    if len(splitName) == 4:
        ct += 1
        fil = open(cog_cross_dir + f, 'r')
        fil.readline()
        fil.readline()
        fil.readline()
        for line in fil:
            src = line.split()[2]
            dst = line.split()[3]
            cross_fil.write(str(NodeMap[splitName[1]][src])+"\t"+str(NodeMap[splitName[2]][dst])+"\n")
            cross_fil.write(str(NodeMap[splitName[2]][dst])+"\t"+str(NodeMap[splitName[1]][src])+"\n")
            cross_fil1.write(str(NodeMap[splitName[1]][src])+"\t"+str(NodeMap[splitName[2]][dst])+"\n")
            num_edges += 1


types = [
'neighborhood',
'neighborhood_transferred',
'fusion',
'cooccurence',
'homology',
'coexpression',
'coexpression_transferred',
'experiments',
'experiments_transferred',
'database',
'database_transferred',
'textmining',
'textmining_transferred',
#'combined_score',
]
for t in types:
    directory = 'output/' + t + '_crossnet/'
    for f in os.listdir(directory):
        splitName = f.split('-')
        if len(splitName) == 4:
            ct += 1
            assert(splitName[1] ==splitName[2]), "Not same"
            fil = open(directory + f, 'r')
            fil.readline()
            fil.readline()
            fil.readline()
            for line in fil:
                src = line.split()[2]
                dst = line.split()[3]
                cross_fil.write(str(NodeMap[splitName[1]][src])+"\t"+str(NodeMap[splitName[2]][dst])+"\n")
                cross_fil.write(str(NodeMap[splitName[2]][dst])+"\t"+str(NodeMap[splitName[1]][src])+"\n")
                cross_fil1.write(str(NodeMap[splitName[1]][src])+"\t"+str(NodeMap[splitName[2]][dst])+"\n")
                end = time.time()
                num_edges += 1

cross_fil.close()
end = time.time()
print "crossnets - ",ct, ", ",num_edges," edges, time: ", end-start
# Save the graph
