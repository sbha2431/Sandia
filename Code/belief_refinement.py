__author__ = 'sudab'

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gridworld import *
import counterexample_parser
import grid_partition
import Slugs_input
import Salty_input
import subprocess
import time
import copy
import counterexample_parser
import visibility

visited_set = set()   # stores already visited nodes
belief_violated_set = set() # stores nodes in whose subtree all leaves vioalte the threshold constraint

belief_true_next = set()
true_plus_vis_next = set()

'''
stores information about the path in the counterexample tree along which we will refine
each element of the list is a set of partitions forming the belief in the current position
'''
toRefine_belief = list()
toRefine_ltl = dict()

def analyse_counterexample(fname,gwg,partitionGrid,beliefcons):
    global visited_set
    global belief_violated_set

    global belief_true_next
    global true_plus_vis_next
     
    global toRefine_belief
    global toRefine_ltl
    
        
    visited_set = set()
    belief_violated_set = set()

    belief_true_next = set()
    true_plus_vis_next = set()
    
    toRefine_belief = list() 
    toRefine_ltl = dict() 
        
    with open(fname) as f:
        content = f.readlines()
    content = [x.strip() for x in content]

    xstates = list(set(gwg.states) - set(gwg.edges))
    allstates = copy.deepcopy(xstates)
    beliefcombs = counterexample_parser.powerset(partitionGrid.keys())
    for i in range(gwg.nstates,gwg.nstates+ len(beliefcombs)):
        allstates.append(i)

    def traverse_counterexample(fname,gwg,partitionGrid,beliefcons,ind,agentstate_parent):

        global visited_set
        global belief_violated_set 
        
        global belief_true_next
        global true_plus_vis_next
        
        global toRefine_belief
        global toRefine_ltl
        
        visited_set.add(ind)          
        #print 'INDEX IN COUNTEREXAMPLE ', ind
    
        envstatebin = []
        agentstatebin = []
        beliefstate = set()
        
        line = content[ind].split(' ')
        for r in line[6::]:
            if r[1] == 'y' or r[0] == 'y':
                envstatebin.append(r[-2])
            elif r[1] == 'x' or r[0] == 'x':
                agentstatebin.append(r[-2])
        
        # agent position
        if len(agentstatebin) > 0:
            agentstate = xstates[int(''.join(str(e) for e in agentstatebin)[::-1], 2)]
            #print 'Agent position is ', agentstate
        else: # failure state
            return (set(),False)
        if content[ind+1] == 'With no successors.': # terminal state
            return (set(),False)

        # environment position
        envstate = int(''.join(str(e) for e in envstatebin)[::-1],2)
        if envstate < len(xstates):
            belief_true = {xstates[envstate]}
            true_plus_vis = {xstates[envstate]}
            #print 'Environment position is ', xstates[envstate]
        else:
            for b in beliefcombs[envstate - len(xstates)]:
                beliefstate = beliefstate.union(partitionGrid[b])
            belief_true = copy.deepcopy(belief_true_next)
            true_plus_vis = copy.deepcopy(true_plus_vis_next)
            #print 'Environment position is ', beliefstate    
        
        # compute true belief for successor nodes w.r.t. current position of agent
        belief_true_next = set()
        for s in belief_true:
            for a in gwg.actlist:
                for t in np.nonzero(gwg.prob[a][s])[0]:
                    belief_true_next.add(t)
        belief_true_next = belief_true_next - set(gwg.walls)
        true_plus_vis_next = copy.deepcopy(belief_true_next)
        belief_true_next = belief_true_next.intersection(visibility.invis(gwg,agentstate))    

      
        if len(beliefstate) > 0:
            
            # invisible states in belief w.r.t. previous position of agent
            belief_invisible = beliefstate.intersection(visibility.invis(gwg,agentstate_parent))
        
            if (len(beliefstate) > len(belief_true)):
                # belief state imprecise: possibly refine for LTL spec
                if not toRefine_ltl:
                    for b in beliefcombs[envstate - len(xstates)]:
                        if b in toRefine_ltl:
                            toRefine_ltl[b].append(belief_true)
                        else:
                            toRefine_ltl[b] = list()
                            toRefine_ltl[b].append(belief_true)
                            
            if len(belief_invisible) > beliefcons: # belief violates constraint
                
                belief_violated_set.add(ind)
                
                if len(belief_true) <= beliefcons: # true belief satisfies constraint
                    
                    print 'Invisible states in belief:', belief_invisible
                    print "Precise belief:", belief_true
                    
                    # partitions in the leaf node that will be refined
                    tr = set()
                    for b in beliefcombs[envstate - len(xstates)]:
                        tr.add(b)
                    toRefine_belief.append(tr)
                    
                    leaf_belief = copy.deepcopy(true_plus_vis)
                    return (leaf_belief,True)
                else:
                    return (set(),True)     
        
        
        '''
        recurse over the successors (subtrees) of the current node, searching for a leaf node to refine
        if in some subtree such node is found, add the current node to the counterexample and return 
        '''
        belief_violated = True
        belief_true_next_current = copy.deepcopy(belief_true_next)
        nextposstates = map(int,content[ind+1][18:].split(', '))
        for succ in range(0,len(content),2):
            if (int(content[succ].split(' ')[1]) in nextposstates):
                if (succ not in visited_set):
                    belief_true_next = copy.deepcopy(belief_true_next_current)
                    (leaf_belief,belief_violated_rec) = traverse_counterexample(fname,gwg,partitionGrid,beliefcons,succ,agentstate)
                    belief_violated = (belief_violated and belief_violated_rec)
                    if toRefine_belief:
                        tr = set()
                        if envstate >= len(xstates):
                            for b in beliefcombs[envstate - len(xstates)]:
                                tr.add(b)
                        toRefine_belief.append(tr)
                        return (leaf_belief,False)
                else:
                    belief_violated  = (belief_violated and (succ in belief_violated_set))
        if belief_violated:
            belief_violated_set.add(ind) 
        return (set(),belief_violated)
        

    (leaf_belief,belief_violated) = traverse_counterexample(fname,gwg,partitionGrid,beliefcons,0,gwg.current)
    
    return (toRefine_belief,leaf_belief,belief_violated,toRefine_ltl)
    
