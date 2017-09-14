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
import counterexample_parser
import copy

slugs = '/home/sudab/Applications/slugs/src/slugs'

def cegar_loop(gwg,moveobstacles,velocity,beliefparts,infile,outfile,cexfile,belief_safety,belief_liveness,target_reachability,partition_init = dict(),local_refinement=False, precise_refinement=False):
    start_time = time.time()
    conv_time = 0
    if len(partition_init) > 0:
        partition = copy.deepcopy(partition_init)
    else:
        partition = grid_partition.partitionGrid(gwg,beliefparts);

    if target_reachability: # check realizability of the LTL specification under full observability
        print ('Writing slugs input file...')
        filename = 'slugs_input_'+str(gwg.nagents)+'agents.structuredslugs'
        Salty_input.write_to_slugs_fullobs(infile,gwg,moveobstacles[0],velocity)
        print ('Converting input file...')
        conv_time_start = time.time()
        os.system('python compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
        conv_time += time.time() - conv_time_start
        print('Checking realizability of LTL spec ...')
        sp = subprocess.Popen(slugs + ' --counterStrategy ' + infile+'.slugsin > ' + cexfile,shell=True, stdout=subprocess.PIPE)
        sp.wait()
    
        if (os.stat(cexfile).st_size > 0):
            print 'LTL specification is not realizable.'
            return 
        else:    
            print 'LTL specification is realizable.'
        
    done = False
    realizable = False
    iteration = 1
    
    
    
    while (not done):

        print 'ITERATION ', iteration
        print 'PARTITION', partition
        
        partition_local = copy.deepcopy(partition)
        
        # check realizability of the full spec
        print ('Writing slugs input file...')
        Salty_input.write_to_slugs_part(infile,gwg,moveobstacles[0],velocity, partition,belief_safety,belief_liveness,target_reachability)
        print ('Converting input file...')
        conv_time_start = time.time()
        os.system('python compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
        conv_time += time.time() - conv_time_start
        print('Checking realizability of full spec...')
        sp = subprocess.Popen(slugs + ' --counterStrategy ' + infile+'.slugsin > ' + cexfile,shell=True, stdout=subprocess.PIPE)
        sp.wait()
        
        done = (os.stat(cexfile).st_size == 0)
            
        if (done): # no counterexample found
            realizable=True
            break;
    
        # check if the counterexample is spurious
        
        (refinement,toRefine,refine_states,neg_states_0,prefix_length) = belief_refinement.analyse_counterexample(cexfile,gwg,partition,belief_safety,belief_liveness,target_reachability,gwg.targets[0])
        
        if (not (refinement == 'safety' or refinement == 'liveness') and not target_reachability):
            print 'Belief constraint not realizable'
            break
            
        if not toRefine:
            print 'No further refinement possible'
            break
        
        if toRefine: # refine belief abstraction
    
            if refinement == 'safety' or refinement == 'liveness':
                print 'REFINING DUE TO BELIEF CONSTRAINT OBJECTIVE'
            if refinement == 'ltl':
                print 'REFINING DUE TO LVENESS OBJECTIVE'

       
            refinement_map_precise  = dict() # maps abstract partitions to lists of state sets with which to refine
            refinement_map_coarse  = dict()  # maps abstract partitions to lists of state sets with which to refine
            neg_states = set()       # set of states that are propagated backwards along the counterexample path
            negstates_map = dict()
                        
            tr_0 = toRefine.pop(0)

            for k in tr_0:
                if not k in refinement_map_precise:
                    refinement_map_precise[k] = list()
                refinement_map_precise[k].append(refine_states)
                refinement_map_precise[k].append(neg_states_0)
                if k in negstates_map:
                    negstates_map[k] = negstates_map[k].union(neg_states_0)
                else:
                    negstates_map[k] = neg_states_0

            '''
            initialize neg_states to be the set of states that are in the abstract belief, 
            but not in the most precise belief for the leaf node of the counterexample path
            '''
            neg_states = neg_states_0
            ''' 
            propagate the refinement information backwards along toRefine until
            a singleton belief or the root node of the tree is reached
            '''
            for tr in toRefine:
                if not tr and (refinement=='safety' or refinement == 'ltl'):
                    break
                if not tr and refinement=='liveness':
                    toRefine_prefix = toRefine[prefix_length:len(toRefine)]
                    break
              
                neg_succ = neg_states
                neg_states = set()
                # propagate refinement set backwards
                all_states = set()
                for k in tr: 
                    for s in partition[k]:
                        all_states.add(s)
                        for a in gwg.actlist:
                            t = set (np.nonzero(gwg.prob[a][s])[0])
                            if t.intersection(neg_succ):
                                neg_states.add(s)
                if not all_states <= neg_states:
                    # store states in refinement_map_precise and negstates_map
                    for k in tr:
                        if k in refinement_map_precise:
                            refinement_map_precise[k].append(neg_states)
                        else:
                            refinement_map_precise[k] = list()
                            refinement_map_precise[k].append(neg_states)
                        if k in negstates_map:
                            negstates_map[k] = negstates_map[k].union(neg_states)
                        else:
                            negstates_map[k] = neg_states
                if local_refinement and (partition_local == partition):            
                    for k in refinement_map_precise.iterkeys():
                        partition_local  = grid_partition.refine_partition(partition_local,k,refinement_map_precise[k])
                    
            if refinement == 'liveness' and prefix_length > 0:
                tr = toRefine_prefix.pop(0)
                neg_states = neg_states_0
                ''' 
                propagate the refinement information backwards along toRefine until
                a singleton belief or the root node of the tree is reached
                '''
                for tr in toRefine_prefix:
                    if not tr:
                        break
                    neg_succ = neg_states
                    neg_states = set()
                    # propagate refinement set backwards
                    all_states = set()
                    for k in tr: 
                        for s in partition[k]:
                            all_states.add(s)
                            for a in gwg.actlist:
                                t = set (np.nonzero(gwg.prob[a][s])[0])
                                if t.intersection(neg_succ):
                                    neg_states.add(s)
                    if not all_states <= neg_states:            
                        # store set in refinement_map_precise or negstates_map
                        for k in tr:
                            if k in refinement_map_precise:
                                refinement_map_precise[k].append(neg_states)
                            else:
                                refinement_map_precise[k] = list()       
                                refinement_map_precise[k].append(neg_states)
                            if k in negstates_map:
                                negstates_map[k] = negstates_map[k].union(neg_states)
                            else:
                                negstates_map[k] = neg_states
                    if local_refinement and (partition_local == partition):
                        for k in refinement_map_precise.iterkeys():
                            partition_local  = grid_partition.refine_partition(partition_local,k,refinement_map_precise[k])
            
            'constrcut efinement_map_coarse'
            for k in tr_0:
                if not k in refinement_map_coarse:
                    refinement_map_coarse[k] = list()
                refinement_map_coarse[k].append(refine_states)
                
            for k in negstates_map.iterkeys():
                if not k in refinement_map_coarse:
                    refinement_map_coarse[k] = list()
                refinement_map_coarse[k].append(negstates_map[k])
                
            #print 'REF MAP PRECISE', refinement_map_precise    
            #print 'REF MAP COARSE', refinement_map_coarse
            
            '''
            split each of the partitions k in refinement_map_coarse according to the
            list refinement_map_coarse[k] of sets of concrete states 
            '''
            for k in refinement_map_coarse.iterkeys():
                partition_coarse  = grid_partition.refine_partition(partition,k,refinement_map_coarse[k])
            if precise_refinement or partition_coarse == partition:
                if not precise_refinement and local_refinement and not (partition_local == partition):
                    print 'USING LOCAL BELIEF REFINEMENT'
                    partition = copy.deepcopy(partition_local)
                else:    
                    print 'USING PRECISE BELIEF REFINEMENT'
                    '''
                    split each of the partitions k in refinement_map_precise according to the
                    list refinement_map_precise[k] of sets of concrete states 
                    '''
                    for k in refinement_map_precise.iterkeys():
                        partition  = grid_partition.refine_partition(partition,k,refinement_map_precise[k])
            else:
                partition = copy.deepcopy(partition_coarse)
                print 'USING COARSE BELIEF REFINEMENT'
        else: 
            break
        iteration = iteration+1

    if(not realizable):
        print('Specification is not realizable')
        print('Simulating counter-strategy ...')
        counterexample_parser.run_counterexample_part(cexfile,gwg,partition)
        
    else: 
        # compute controller for realizable abstraction

        #Salty_input.write_to_slugs_part(infile,gwg,moveobstacles[0],velocity, partition,belief_safety,belief_liveness,target_reachability)
        #print ('Converting input file...')
        #os.system('python compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
        print('Computing controller...')
        sp = subprocess.Popen(slugs + ' --explicitStrategy --jsonOutput ' + infile + '.slugsin > '+ outfile,shell=True, stdout=subprocess.PIPE)
        sp.wait()
        print('Simulating controller ...')
        print 'Total time taken is ', time.time() - start_time, ' s'
        print 'Total time taken for file conversion is ', conv_time, ' s'
        print 'Actual time taken is ', (time.time() - start_time) - conv_time, ' s'
        simulateController.userControlled_partition(outfile,gwg,partition,moveobstacles)
        



