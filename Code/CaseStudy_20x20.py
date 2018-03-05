__author__ = 'sudab'

from gridworld import *
import Salty_input
import os
import subprocess
import simulateController
import pickle
import visibility

slugs = '/home/sudab/Applications/slugs/src/slugs'
# Define gridworld parameters
nrows = 20
ncols = 20
nagents = 6
initial = [44,54,182,282,310,237]
targets = [[],[],[],[],[],[]]
obstacles = [80,81,102,123,124,145,146,147,148,149,150,151,260,241,242,243,224,225,206,207,208,380,361,342,323,304,288,269,270,251,232,213,194,175,196,217,
             154,155,156,157,158,159,236,255,274,294,313,333,49,50,51,69,70,71]
moveobstacles = [46]

allowed_states = [[None]]*nagents
allowed_states[0] = [0,1,2,3,4,5,6,7,8,9,10,20,21,22,23,24,25,26,27,28,29,30,40,41,42,43,44,45,46,47,48,60,61,62,63,64,65,66,67,68,
                        82,83,84,85,86,87,88,89,90,103,104,105,106,107,108,109,110,125,126,127,128,129,130]
allowed_states[1] = [10,11,12,13,14,15,16,17,18,19,30,31,32,33,34,35,36,37,38,39,52,53,54,55,56,57,58,59,72,73,74,75,76,77,78,79,
                     90,91,92,93,94,95,96,97,98,99,110,111,112,113,114,115,116,117,118,119,130,131,132,133,134,135,136,137,138,139,152,153]
allowed_states[2] = [100,101,120,121,122,140,141,142,143,144,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,
                     180,181,182,183,184,185,186,187,188,189,190,191,192,193,
                     200,201,202,203,204,205,220,221,222,223,240,209,210,211,212,152,153]
allowed_states[3] = [209,210,211,212,226,227,228,229,230,231,244,245,246,247,248,249,250,261,262,263,264,265,266,267,268,
                     280,281,282,283,284,285,286,287,300,301,302,303,305,306,307,320,321,322,340,341,360]
allowed_states[4] = [195,214,215,216,233,234,235,252,253,254,271,272,273,289,290,291,292,293,305,306,307,308,309,310,311,312,
                     324,325,326,327,328,329,330,331,332,343,344,345,346,347,348,349,350,351,352,353,
                     362,363,364,365,366,367,368,369,370,371,372,373,
                     381,382,383,384,385,386,387,388,389,390,391,392,393]
allowed_states[5] = [176,177,178,179,197,198,199,218,219,237,238,239,256,257,258,259,275,276,277,278,279,
                     295,296,297,298,299,314,315,316,317,318,319,334,335,336,337,338,339,353,354,355,356,357,358,359,
                     373,374,375,376,377,378,379,393,394,395,396,397,398,399]

fullvis_states = [[],[],[],
                  [],[],[]]

# partialvis_states = [{0:{10,30},1:{90,110,130}} ,{0:{10,30},1:{90,110,130},2:{152,153}}, {0:{152,153},1:{209,210,211,212}},
#                      {0:{209,210,211,212},1:{305,306,307}}, {0:{305,306,307},1:{353,373,393}} ,{0:{353,373,393}} ]

partialvis_states = [{0:{10,30,90,110,130}} ,{0:{10,30,90,110,130,152,153}}, {0:{152,153,209,210,211,212}},
                     {0:{209,210,211,212,305,306,307}}, {0:{305,306,307,353,373,393}} ,{0:{353,373,393}} ]

regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]
gwg.render()

gwg.draw_state_labels()

partitionGrid0 = dict()
partitionGrid1 = dict()
partitionGrid2 = dict()
partitionGrid3 = dict()
partitionGrid4 = dict()
partitionGrid5 = dict()
partitionGrid0[(0,0)] = [0,1,2,3,4,20,21,22,23,24,40,41,42,43,44,60,61,62,63,64,82,83,84,103,104]
partitionGrid0[(0,1)] = [5,6,7,8,9,10,25,26,27,28,29,30,45,46,47,48]
partitionGrid0[(1,1)] = [65,66,67,68,85,86,87,88,89,90,105,106,107,108,109,110,125,126,127,128,129,130]
partitionGrid1[(0,0)] = [10,11,12,13,30,31,32,33,52,53]
partitionGrid1[(1,0)] = [72,73,90,91,92,93,110,111,112,113,130,131,132,133,152,153]
partitionGrid1[(2,0)] = [14,15,16,17,18,19,34,35,36,37,38,39,54,55,56,57,58,59]
partitionGrid1[(3,0)] = [74,75,76,77,78,79,94,95,96,97,98,99,114,115,116,117,118,119,
                        134,135,136,137,138,139]
partitionGrid2[(0,0)] = [100,101,120,121,122,140,141,142,143,144]
partitionGrid2[(1,0)] = [200,201,202,203,204,205,220,221,222,223,240]
partitionGrid2[(2,0)] = [160,161,162,163,164,165,180,181,182,183,184,185]
partitionGrid2[(3,0)] = [166,167,168,169,170,186,187,188,189,190,209,210]
partitionGrid2[(4,0)] = [152,153,171,172,173,174,191,192,193,211,212]
partitionGrid2[(5,0)] = [90,91,92,93,94,95,96,97,98,99,110,111,112,113,114,115,116,117,118,119,130,131,132,133,134,135,136,137,138,139,
                        150,151,152,156,157,158,159]
partitionGrid3[(0,0)] = [209,210,211,212,229,230,231,249,250]
partitionGrid3[(1,0)] = [226,227,228,246,247,248,266,267,268,286,287,305,306,307]
partitionGrid3[(2,0)] = [244,245,263,264,265,283,284,285,303]
partitionGrid3[(3,0)] = [261,262,280,281,282,300,301,302,320,321,322,340,341,360]
partitionGrid4[(0,0)] = [195,214,215,216,233,234,235,252,253,254]
partitionGrid4[(1,0)] = [271,272,273,291,292,293,311,312,331,332]
partitionGrid4[(5,0)] = [351,352,353,371,372,373,391,392,393]
partitionGrid4[(2,0)] = [289,290,308,309,310,328,329,330,348,349,350,368,369,370,388,389,390]
partitionGrid4[(3,0)] = [305,306,307,325,326,327,345,346,347,365,366,367,385,386,387]
partitionGrid4[(4,0)] = [324,343,344,362,363,364,381,382,383,384]
partitionGrid5[(0,0)] = [176,177,178,179,197,198,199,218,219,237,238,239]
partitionGrid5[(1,0)] = [256,257,258,259,275,276,277,278,279,295,296,297,298,299]
partitionGrid5[(2,0)] = [314,315,334,335,353,354,355,373,374,375,393,394,395]
partitionGrid5[(3,0)] = [316,317,318,319,336,337,338,339,356,357,358,359,376,377,378,379,396,397,398,399]

pg = [partitionGrid0,partitionGrid1,partitionGrid2,partitionGrid3,partitionGrid4,partitionGrid5]

# gwg.save('gridworldfig.png')
visdist = [4,4,4,4,4,4]
vel = [2,2,2,2,2,2]
print 'Writing input file...'
invisibilityset = []
filename = []
for n in range(gwg.nagents):
    # iset = dict.fromkeys(set(gwg.states),frozenset({gwg.nrows*gwg.ncols+1}))
    # for s in set(gwg.states):
    #     iset[s] = visibility.invis(gwg,s,visdist[n]).intersection(set(allowed_states[n]))
    #     iset[s] = iset[s] - set(fullvis_states[n])
    #     if s in gwg.obstacles:
    #         iset[s] = {-1}
    # pickle_out = open("dict{}.pickle".format(n),"wb")
    # pickle.dump(iset, pickle_out)
    # pickle_out.close()
    pickle_in = open("dict{}.pickle".format(n),"rb")
    iset = pickle.load(pickle_in)
    invisibilityset.append(iset)
    outfile = 'test3{}.json'.format(n)
    infile = 'test3{}'.format(n)
    filename.append(outfile)
    print 'output file: ', outfile
    print 'input file name:', infile
    Salty_input.write_to_slugs_part_dist_impsensors(infile,gwg,initial[n],moveobstacles[0],iset,targets[n],vel[n],visdist[n],allowed_states[n],fullvis_states[n],partialvis_states[n],
                                                pg[n], belief_safety = 0, belief_liveness = 5, target_reachability = False)
    # # #
    print ('Converting input file...')
    os.system('python compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
    print('Computing controller...')
    sp = subprocess.Popen(slugs + ' --explicitStrategy --jsonOutput ' + infile + '.slugsin > '+ outfile,shell=True, stdout=subprocess.PIPE)
    sp.wait()


simulateController.userControlled_partition_dist_imp_sensor(filename,gwg,pg,moveobstacles,allowed_states,invisibilityset,partialvis_states)
