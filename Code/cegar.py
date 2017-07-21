__author__ = 'sudab'

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gridworld import *
import belief_refinement
import grid_partition
import Slugs_input
import Salty_input
import subprocess
import time
import simulateController

slugs = '/home/rayna/work/tools/slugs/src/slugs'

def cegar_loop(gwg,moveobstacles,beliefcons,beliefparts,infile,outfile,cexfile):

    partition = grid_partition.partitionGrid(gwg,beliefparts);

    done= False
    realizable = False
    iteration = 1

    while (not done):

        print 'ITERATION ', iteration
        print 'PARTITION', partition
    
        # check realizability
    
        print ('Writing slugs input file...')
        Salty_input.write_to_slugs_part(infile,gwg,moveobstacles[0],1, partition,beliefcons)
        print ('Converting input file...')
        os.system('python compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
        print('Checking realizability...')
        subprocess.Popen(slugs + ' --counterStrategy ' + infile+'.slugsin > ' + cexfile,shell=True, stdout=subprocess.PIPE)

        time.sleep(10)

        done = (os.stat(cexfile).st_size == 0)

        if (done):
            realizable=True
            break;
    
        # check if counterexample is spurious
        
        (res,leafBelief,toRefine) = belief_refinement.analyse_counterexample(cexfile,gwg,partition,beliefcons)
        if(not res):
            break

        # refine belief abstraction
    
        # OLD REFINEMENT: based only on a leaf node in the tree 
        '''
        for k in refineLeaf:
            partition = grid_partition.partitionState_manual(partition,k,leafBelief)
        '''
        # OLD REFINEMENT: ends here
        
        # NEW REFINEMENT: propagating the refinement of the leaf backwards on the path
        
        refinement_map  = dict() # maps abstract partitions to lists or state sets with which to refine
        neg_states = set()       # set of states that are propagated backwards along the counterexample path
        
        '''
        initialize neg_states to be the set of states that are in the abstract belief, 
        but not in the most precise belief for the leaf node of the counterexample path
        '''
        Leaf = toRefine.pop(0)
        for k in Leaf:
            neg_states = neg_states.union(partition[k].difference(leafBelief))
            refinement_map[k] = list()
            refinement_map[k].append(leafBelief)
        
        
        ''' 
        propagate the refinement information backwards along toRefine until
        a singleton belief or the root node of the tree is reached
        '''
        for tr in toRefine:
            if not tr:
                break
            neg_succ = neg_states
            neg_states = set()
            # propagate refinement set backwards
            for k in tr: 
                for s in partition[k]:
                    for a in gwg.actlist:
                        t = set (np.nonzero(gwg.prob[a][s])[0]) - set(gwg.obstacles)
                        if t.intersection(neg_succ):
                            neg_states.add(s)
            # store set in refinement_map        
            for k in tr:
                if k in refinement_map:
                    refinement_map[k].append(neg_states)
                else:
                    refinement_map[k] = list()
                    refinement_map[k].append(neg_states)
        
        print 'REF MAP', refinement_map

        '''
        split each of the partitions k in refinement_map according to the
        list refinement_map[k] of sets of concrete states 
        '''
        for k in refinement_map.iterkeys():
            partition  = grid_partition.refine_partition(partition,k,refinement_map[k])
        
        # NEW REFINEMENT: ends here
        
        iteration = iteration+1

    if(not realizable):
        print('Specification is not realizable')
    else:
        # compute controller for realizable abstraction

        Salty_input.write_to_slugs_part(infile,gwg,moveobstacles[0],1, partition,beliefcons)
        print ('Converting input file...')
        os.system('python compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
        print('Computing controller...')
        subprocess.Popen(slugs + ' --explicitStrategy --jsonOutput ' + infile + '.slugsin > '+ outfile,shell=True, stdout=subprocess.PIPE)
        time.sleep(10)
        print('Simulating controller ...')
        
        simulateController.userControlled_partition(outfile,gwg,partition,moveobstacles)
        


