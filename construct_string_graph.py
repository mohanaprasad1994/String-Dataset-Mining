import sys
sys.path.insert(0, './../../swig/')
import snap
import argparse
import logging
import os
import time

parser = argparse.ArgumentParser(description='Generate a Multi-Modal Network')
parser.add_argument('--output_dir', help='output path to save the Multi-Modal Network', default='.')
parser.add_argument('--loglevel', help='info for debug print.')
args = parser.parse_args()
if args.loglevel:
    numeric_level = getattr(logging, args.loglevel.upper(), None)
    logging.basicConfig(level=numeric_level)

context = snap.TTableContext()
# Construct the graph
logging.info('Building String Multi-Modal Network')
Graph = snap.TMMNet.New()

start = time.time()
ct = 0
mode_time = 0.0
mode_dir = 'output/modes'
# Loading Modes (Gene)
for f in os.listdir('output/modes'):
    splitName = f.split('-')
    if len(splitName) == 3:
        ct += 1
        modeId = splitName[1] + 'Id'
        schema = snap.Schema()
        schema.Add(snap.TStrTAttrPr(modeId, snap.atStr))
        schema.Add(snap.TStrTAttrPr("datasetId", snap.atStr))
        mode = snap.TTable.LoadSS(schema, mode_dir + '/' + f, context, "\t", snap.TBool(False))
        logging.info('Done loading %s Mode' % splitName[1])
        start2 = time.time()
        snap.LoadModeNetToNet(Graph, splitName[1], mode, modeId, snap.TStr64V())
        end2 = time.time()
        mode_time += end2 - start2
end = time.time()
print "modes - ",ct, " Total time including table loading ", end-start
print "table loading time for modes creation: ", end-start-mode_time
print "time for modes creation without table load time: ", mode_time

start = time.time()
ct = 0
cross_time = 0.0
# Loading Cross-Nets
cog_cross_dir = 'output/cog_crossnet/'
for f in os.listdir('output/cog_crossnet'):
    splitName = f.split('-')
    if len(splitName) == 4:
    	ct += 1
        edgeId = "Cog" + splitName[1] + 'Id'
        schema = snap.Schema()
        schema.Add(snap.TStrTAttrPr(edgeId, snap.atStr))
        schema.Add(snap.TStrTAttrPr("datasetId", snap.atStr))
        schema.Add(snap.TStrTAttrPr(splitName[1] + "SrcId", snap.atStr))
        schema.Add(snap.TStrTAttrPr("CogDstId", snap.atStr))
        crossnet = snap.TTable.LoadSS(schema, cog_cross_dir + f, context, "\t", snap.TBool(False))
        logging.info('Done loading %s-COG Cross-Net' % splitName[1])
        start2 = time.time()
        Graph.AddCrossNet(splitName[1], "COG", "Cog" + splitName[1], False)
        snap.LoadCrossNetToNet(Graph, splitName[1], "COG", "Cog" + splitName[1], crossnet, splitName[1] + "SrcId", "CogDstId", snap.TStr64V())
        end2 = time.time()
        cross_time += end2 - start2
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
            edgeId = splitName[1] + '-' + splitName[1] + 'Id'
            schema = snap.Schema()
            schema.Add(snap.TStrTAttrPr(edgeId, snap.atStr))
            schema.Add(snap.TStrTAttrPr("datasetId", snap.atStr))
            schema.Add(snap.TStrTAttrPr(splitName[1] + "SrcId", snap.atStr))
            schema.Add(snap.TStrTAttrPr(splitName[1] + "DstId", snap.atStr))
            crossnet = snap.TTable.LoadSS(schema, directory + f, context, "\t", snap.TBool(False))
            logging.info('Done loading %s-%s-%s Cross-Net' % (t, splitName[1], splitName[1]))
            start2 = time.time()
            Graph.AddCrossNet(splitName[1], splitName[1], t + '-' + splitName[1] + '-' + splitName[1], False)
            snap.LoadCrossNetToNet(Graph, splitName[1], splitName[1], t + '-' + splitName[1] + '-' + splitName[1], crossnet, splitName[1] + "SrcId", splitName[1] + "DstId", snap.TStr64V())
            end2 = time.time()
            cross_time += end2 - start2
end = time.time()
print "crossnets - ",ct, " total time including table load time ", end-start
print "time to load crossnet tables ", end-start - cross_time
print "time to add crossnets without table load time ", cross_time
# Save the graph
start = time.time()
logging.info('Saving Multi-Modal Network to disk')
outputPath = os.path.join(args.output_dir, "string_full1.graph")
FOut = snap.TFOut(outputPath)
Graph.Save(FOut)
FOut.Flush()

end = time.time()
print "Saving graph - ","Time: ", end-start