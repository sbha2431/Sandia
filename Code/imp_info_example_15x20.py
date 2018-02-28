__author__ = 'sudab'

from gridworld import *
import Salty_input
import os
import subprocess
import simulateController
slugs = '/home/sudab/Applications/slugs/src/slugs'
# Define gridworld parameters
nrows = 15
ncols = 20
nagents = 5
initial = [44,222,73,237,190]
targets = [[21],[200],[110],[],[251]]
obstacles = [153,154,155,173,174,175,193,194,195,213,214,215,233,234,235,68,69,88,89,108,109,128,129,183,184,185,186,187,203,204,205,206,207,223,224,225,226,227]
moveobstacles = [197]

allowed_states = [[None]]*nagents
allowed_states[0] = [0,1,2,3,4,5,6,7,8,9,20,21,22,23,24,25,26,27,28,29,40,41,42,43,44,45,46,47,48,49,60,61,62,63,64,65,66,67,
                        80,81,82,83,84,85,86,87,100,101,102,103,104,105,106,107,120,121,122,123,124,125,126,127,
                        140,141,142,143,144,145,146,147,148,160,161,162,163,164,165,166,167,168,180,181,182]
allowed_states[1] = [180,181,182,188,200,201,202,208,220,221,222,228,240,241,242,243,244,245,246,247,248,
                        260,261,262,263,264,265,266,267,268,280,281,282,283,284,285,286,287,288]
#
allowed_states[2] = [8,9,10,11,12,13,14,15,16,17,18,19,28,29,30,31,32,33,34,35,36,37,38,39,48,49,50,51,52,53,54,55,56,57,58,59,70,71,72,73,74,75,76,77,78,79,
                        90,91,92,93,94,95,96,97,98,99,110,111,112,113,114,115,116,117,118,119,130,131,132,133,134,135,136,137,138,139,
                        150,151,152,156,157,158,159]
allowed_states[3] = [156,157,158,159,176,177,178,179,196,197,198,199,216,217,218,219,
                        236,237,238,239,253,254,255,256,257,258,259,273,274,275,276,277,278,279,
                        293,294,295,296,296,297,298,299]
allowed_states[4] = [148,149,150,151,152,168,169,170,171,172,188,189,190,191,192,208,209,210,211,212,228,229,230,231,232,248,249,250,251,252,253,
                         268,269,270,271,272,273,288,289,290,291,292,293]

fullvis_states = [[],[],
                  [],[],[]]

partialvis_states = [{0:{8,9,28,29,48,49,148,168,180,181,182}} ,{0:{180,181,182,188,208,228,248,268,288}}, {0:{8,9,28,29,48,49,150,151,152,156,157,158,159}},
                     {0:{156,157,158,159,253,273,293}}, {0:{148,168,188,208,228,248,268,288,253,273,293,150,151,152}}  ]

# partialvis_states = [{0:{8,9,28,29,48,49}, 1:{148,168} , 2:{180,181,182}} ,{0:{180,181,182}, 1:{188,208,228,248,268,288}}, {0:{8,9,28,29,48,49}, 1:{150,151,152} , 2:{156,157,158,159}},
#                      {0:{156,157,158,159}, 1:{253,273,293}}, {0:{148,168,188,208,228,248,268,288}, 1:{253,273,293} , 2:{150,151,152}}  ]


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
partitionGrid0[(0,0)] = [0,1,2,3,4,5,6,7,8,9,20,21,22,23,24,25,26,27,28,29,40,41,42,43,44,45,46,47,47,48,49]
partitionGrid0[(1,0)] = [60,61,62,63,64,65,66,67,
                        80,81,82,83,84,85,86,87,100,101,102,103,104,105,106,107]
partitionGrid0[(2,0)] = [120,121,122,123,124,125,126,127,
                        140,141,142,143,144,145,146,147,148]
partitionGrid0[(3,0)] = [160,161,162,163,164,165,166,167,168,180,181,182]
partitionGrid1[(0,0)] = [180,181,182,188,200,201,202,208,220,221,222,228]
partitionGrid1[(1,0)] = [240,241,242,243,244,245,246,247,248,260,261,262,263,264,265,266,267,268,280,281,282,283,284,285,286,287,288]
partitionGrid2[(0,0)] = [8,9,10,11,12,13,14,15,16,17,18,19,28,29,30,31,32,33,34,35,36,37,38,39]
partitionGrid2[(1,0)] = [48,49,50,51,52,53,54,55,56,57,58,59,70,71,72,73,74,75,76,77,78,79]
partitionGrid2[(2,0)] = [90,91,92,93,94,95,96,97,98,99,110,111,112,113,114,115,116,117,118,119,130,131,132,133,134,135,136,137,138,139,
                        150,151,152,156,157,158,159]
partitionGrid3[(0,0)] = [156,157,158,159,176,177,178,179,196,197,198,199,216,217,218,219,
                        236,237,238,239]
partitionGrid3[(1,0)] = [253,254,255,256,257,258,259,273,274,275,276,277,278,279,
                        293,294,295,296,296,297,298,299]
partitionGrid4[(0,0)] = [148,149,150,151,152,168,169,170,171,172,188,189,190,191,192,208,209,210,211,212,228,229,230,231,232]
partitionGrid4[(1,0)] = [248,249,250,251,252,253,
                         268,269,270,271,272,273,288,289,290,291,292,293]

pg = [partitionGrid0,partitionGrid1,partitionGrid2,partitionGrid3,partitionGrid4]

# gwg.save('gridworldfig.png')
visdist = [5,4,6,3,4]
vel = [2,2,2,2,2]
gs = [12,25]
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
    outfile = 'test{}.json'.format(n)
    infile = 'test{}'.format(n)
    filename.append(outfile)
    print 'output file: ', outfile
    print 'input file name:', infile
    iset = Salty_input.write_to_slugs_part_dist_impsensors(infile,gwg,initial[n],moveobstacles[0],targets[n],vel[n],visdist[n],allowed_states[n],fullvis_states[n],partialvis_states[n],
                                                pg[n], belief_safety = 0, belief_liveness = 4, target_reachability = True)
    invisibilityset.append(iset)
    print ('Converting input file...')
    os.system('python compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
    print('Computing controller...')
    sp = subprocess.Popen(slugs + ' --explicitStrategy --jsonOutput ' + infile + '.slugsin > '+ outfile,shell=True, stdout=subprocess.PIPE)
    sp.wait()


simulateController.userControlled_partition_dist_imp_sensor(filename,gwg,pg,moveobstacles,allowed_states,invisibilityset,partialvis_states)


