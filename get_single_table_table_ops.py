### File to read all the tables (modes and crossnets) and generate a single table ( uses snap table operations)

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

# Construct the graph
snap.TTable.SetMP(0)
start = time.time()
ct = 0
mode_time = 0.0
mode_dir = 'output/modes'
ModeTable = None
# Loading Modes (Gene)
for f in os.listdir('output/modes'):
    splitName = f.split('-')
    if len(splitName) == 3:
        context = snap.TTableContext()
        ct += 1
        if splitName[1] == "COG": #Cog mode is numbered 0
            splitName[1] = '0'
        modeId = splitName[1] + 'Id'
        schema = snap.Schema()
        schema.Add(snap.TStrTAttrPr("Id", snap.atInt))
        schema.Add(snap.TStrTAttrPr("datasetId", snap.atInt))
        mode = snap.TTable.LoadSS(schema, mode_dir + '/' + f, context, "\t", snap.TBool(False))
        start2 = time.time()
        num_rows = mode.GetNumRows()
        modeIds = snap.TInt64V(2*num_rows, num_rows, int(splitName[1]) ) ## to optimize. reallocaton every time
        mode.StoreIntCol("Mode", modeIds)
        mode.ColAdd("Id", (int(splitName[1])<<40), "NodeId" )
        Attrs = snap.TStr64V()
        Attrs.Add("NodeId");
        Attrs.Add("Mode");
        Attrs.Add("Id");
        mode = mode.Project(Attrs)
        logging.info('Done loading %s Mode' % splitName[1])
        if not ModeTable:

            ModeTable = mode
        else:
            ModeTable.UnionAllInPlace(mode)
        
        end2 = time.time()
        mode_time += end2 - start2
end = time.time()
print "modes - ",ct, " Total time including table loading ", end-start
print "table loading time for modes creation: ", end-start-mode_time
print "time for mode table creation without table load time: ", mode_time

start = time.time()
logging.info('Saving Mode table to disk')
outputPath = os.path.join(args.output_dir, "mode_table.bin")
FOut = snap.TFOut("mode_table.bin")
ModeTable.Save(FOut)
FOut.Flush()

end = time.time()
print "Saving Mode table as bin - ","Time: ", end-start

tart = time.time()
logging.info('Saving Mode table to disk as tsv')
outputPath = os.path.join(args.output_dir, "mode_table.tsv")
ModeTable.SaveSS("mode_table.tsv")

end = time.time()
print "Saving Mode table as bin - ","Time: ", end-start

mode = None
ModeTable = None

start = time.time()
ct = 0
cross_time = 0.0
crossTable = None
crossnetIdMap = {}
# Loading Cross-Nets
cog_cross_dir = 'output/cog_crossnet/'
for f in os.listdir('output/cog_crossnet'):
    splitName = f.split('-')
    if len(splitName) == 4:
    	ct += 1
        edgeId = "Cog" + splitName[1] + 'Id'
        crossnetIdMap["Cog-" + splitName[1]] = ct
        schema = snap.Schema()
        schema.Add(snap.TStrTAttrPr("Id", snap.atInt))
        schema.Add(snap.TStrTAttrPr("datasetId", snap.atInt))
        schema.Add(snap.TStrTAttrPr(splitName[1]+"SrcId", snap.atInt))
        schema.Add(snap.TStrTAttrPr("DstId", snap.atInt))
        crossnet = snap.TTable.LoadSS(schema, cog_cross_dir + f, context, "\t", snap.TBool(False))
        logging.info('Done loading %s-COG Cross-Net' % splitName[1])
        start2 = time.time()

        num_rows = crossnet.GetNumRows()
        crossnetIds = snap.TInt64V(2*num_rows, num_rows, ct ) ## to optimize. reallocaton every time
        crossnet.StoreIntCol("CrossNet", crossnetIds)
        crossnet.ColAdd(splitName[1]+"SrcId", (int(splitName[1])<<40), "SrcId" )
        #mode.ColAdd("COGDstId", (int(0)<<40), ResAttr=TStr("NodeId") )
        Attrs = snap.TStr64V()
        Attrs.Add("SrcId");
        Attrs.Add("DstId");
        Attrs.Add("CrossNet");
        Attrs.Add("Id");
        crossnet = crossnet.Project(Attrs)
        logging.info('Done loading %s crossnet' % splitName[1])
        if not crossTable:

            crossTable = crossnet
        else:
            crossTable.UnionAllInPlace(crossnet)
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
            crossnetIdMap[t + '-'+splitName[1] + '-' + splitName[1]] = ct
            schema = snap.Schema()
            schema.Add(snap.TStrTAttrPr("Id", snap.atInt))
            schema.Add(snap.TStrTAttrPr("datasetId", snap.atInt))
            schema.Add(snap.TStrTAttrPr(splitName[1] + "SrcId", snap.atInt))
            schema.Add(snap.TStrTAttrPr(splitName[1] + "DstId", snap.atInt))
            crossnet = snap.TTable.LoadSS(schema, directory + f, context, "\t", snap.TBool(False))
            logging.info('Done loading %s-%s-%s Cross-Net' % (t, splitName[1], splitName[1]))
            start2 = time.time()
            num_rows = crossnet.GetNumRows()
            crossnetIds = snap.TInt64V(2*num_rows, num_rows, ct ) ## to optimize. reallocaton every time
            crossnet.StoreIntCol("CrossNet", crossnetIds)
            crossnet.ColAdd(splitName[1]+"SrcId", (int(splitName[1])<<40), "SrcId" )
            crossnet.ColAdd(splitName[1]+"DstId", (int(splitName[1])<<40), "DstId" )
            Attrs = snap.TStr64V()
            Attrs.Add("SrcId");
            Attrs.Add("DstId");
            Attrs.Add("CrossNet");
            Attrs.Add("Id");
            crossnet = crossnet.Project(Attrs)
            logging.info('Done loading %s crossnet' % splitName[1])
            if not crossTable:

                crossTable = crossnet
            else:
                crossTable.UnionAllInPlace(crossnet)
            end2 = time.time()
            cross_time += end2 - start2
end = time.time()
print crossTable.GetNumRows()
print "crossnets - ",ct, " total time including table load time ", end-start
print "time to load crossnet tables ", end-start - cross_time
print "time for crossnets creation without table load time ", cross_time

start = time.time()
logging.info('Saving Crossnet table to disk')
outputPath = os.path.join(args.output_dir, "crossnet_table.bin")
FOut = snap.TFOut(outputPath)
crossTable.Save(FOut)
FOut.Flush()

end = time.time()
print "Saving Crossnet table as bin - ","Time: ", end-start

tart = time.time()
logging.info('Saving Crossnet table to disk as tsv')
outputPath = os.path.join(args.output_dir, "crossnet_table.tsv")
crossTable.SaveSS("crossnet_table.tsv")

end = time.time()
print "Saving Crossnet table as tsv - ","Time: ", end-start

print crossnetIdMap
