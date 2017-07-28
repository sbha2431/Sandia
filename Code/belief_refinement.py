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

visited = set()   # stores already visited nodes
threshold_violated = set()
truebeliefstates = set()
truebeliefstates_next = set()
truebeliefwithvis_next = set()
'''
stores information about the path in the counterexample tree along which we will refine
each element of the list is a set of partitions forming the belief in the current position
'''
toRefine_belief = list()
toRefine_ltl = dict()

def analyse_counterexample(fname,gwg,partitionGrid,beliefcons):
    global visited
    global threshold_violated
    global truebeliefstates
    global truebeliefstates_next
    global truebeliefwithvis_next
     
    global toRefine_belief
    global toRefine_ltl
    
        
    visited = set()
    truebeliefstates = set()
    truebeliefstates_next = set()
    truebeliefwithvis_next = set()
    threshold_violated = set()
    
    toRefine_belief = list() 
    toRefine_ltl = dict() 
        
    with open(fname) as f:
        content = f.readlines()
    content = [x.strip() for x in content]

    def traverse_counterexample(fname,gwg,partitionGrid,beliefcons,ind,agentstate_parent):
        global visited
        global truebeliefstates
        global truebeliefstates_next
        global truebeliefwithvis_next
        global threshold_violated 
        global toRefine_belief
        global toRefine_ltl
        
        visited.add(ind)          

        #print 'INDEX IN COUNTEREXAMPLE ', ind
        
        beliefLeaf = set()
        imprecise = False     

        xstates = list(set(gwg.states) - set(gwg.edges))
        allstates = copy.deepcopy(xstates)
        beliefcombs = counterexample_parser.powerset(partitionGrid.keys())
        for i in range(gwg.nstates,gwg.nstates+ len(beliefcombs)):
            allstates.append(i)
        gwg.colorstates = [set(), set()]
    
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
            return (False,set(),False,False)
        if content[ind+1] == 'With no successors.': # terminal state
            return (False,set(),False,False)

        # environment position
        envstate = int(''.join(str(e) for e in envstatebin)[::-1],2)
        if envstate < len(xstates):
            truebeliefstates = {xstates[envstate]}
            truebeliefwithvis = {xstates[envstate]}
            #print 'Environment position is ', xstates[envstate]
        else:
            for b in beliefcombs[envstate - len(xstates)]:
                beliefstate = beliefstate.union(partitionGrid[b])
            truebeliefstates = copy.deepcopy(truebeliefstates_next)
            truebeliefwithvis = copy.deepcopy(truebeliefwithvis_next)
            #print 'Environment position is ', beliefstate    
            
        # compute true belief set for successor nodes
        truebeliefstates_next = set()
        for s in truebeliefstates:
            for a in gwg.actlist:
                for t in np.nonzero(gwg.prob[a][s])[0]:
                    truebeliefstates_next.add(t)
        truebeliefstates_next = truebeliefstates_next - set(gwg.walls)
        truebeliefwithvis_next = copy.deepcopy(truebeliefstates_next)
        truebeliefstates_next = truebeliefstates_next.intersection(visibility.invis(gwg,agentstate))    

      
        if len(beliefstate) > 0:
            beliefinvisstates = beliefstate.intersection(visibility.invis(gwg,agentstate_parent))
            if (len(beliefinvisstates) > len(truebeliefstates)):
                imprecise = True
                if not toRefine_ltl:
                    for b in beliefcombs[envstate - len(xstates)]:
                        if b in toRefine_ltl:
                            toRefine_ltl[b].append(truebeliefstates)
                        else:
                            toRefine_ltl[b] = list()
                            toRefine_ltl[b].append(truebeliefstates)
                            
            if len(beliefinvisstates) > beliefcons:
                threshold_violated.add(ind)
                if len(truebeliefstates) <= beliefcons:
                    print 'Invisible states in belief states are', beliefinvisstates
                    print "Fully refined belief states are", truebeliefstates
                    
                    # partitions in the leaf node that will be refined
                    tr = set()
                    for b in beliefcombs[envstate - len(xstates)]:
                        tr.add(b)
                    toRefine_belief.append(tr)
                    
                    beliefLeaf = copy.deepcopy(truebeliefwithvis)
                    return (True,beliefLeaf,imprecise,True)
                else:
                    return (False,set(),imprecise,True)     
        '''
        recurse over the successors (subtrees) of the current node, searching for a leaf node to refine
        if in some subtree such node is found, add the current node to the counterexample and return 
        '''
        truebeliefstates_next_current = copy.deepcopy(truebeliefstates_next)
        nextposstates = map(int,content[ind+1][18:].split(', '))
        belief_violated = True
        for succ in range(0,len(content),2):
            if (int(content[succ].split(' ')[1]) in nextposstates):
                if (succ not in visited):
                    truebeliefstates_next = copy.deepcopy(truebeliefstates_next_current)
                    (res,leafBelief,imprecise_rec,belief_violated_rec) = traverse_counterexample(fname,gwg,partitionGrid,beliefcons,succ,agentstate)
                    imprecise = (imprecise or imprecise_rec)
                    belief_violated = (belief_violated and belief_violated_rec)
                    if res:
                        tr = set()
                        if envstate >= len(xstates):
                            for b in beliefcombs[envstate - len(xstates)]:
                                tr.add(b)
                        toRefine_belief.append(tr)
                        return (True,leafBelief,imprecise,False)
                else:
                    belief_violated  = (belief_violated and (succ in threshold_violated))
        if belief_violated:
            threshold_violated.add(ind)                
        return (False,set(),imprecise,belief_violated)
        

    (res,leafBelief,imprecise,belief_violated) = traverse_counterexample(fname,gwg,partitionGrid,beliefcons,0,gwg.current)
    return (res,leafBelief,toRefine_belief,imprecise,belief_violated,toRefine_ltl)
    
