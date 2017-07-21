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
'''
stores information about the path in the counterexample tree along which we will refine
each element of the list is a set of partitions forming the belief in the current position
'''
toRefine = list() 
truebeliefstates = set()

def analyse_counterexample(fname,gwg,partitionGrid,beliefcons):
    global visited
    global toRefine
    global truebeliefstates
    toRefine = list() 
    truebeliefstates = set()
    
    with open(fname) as f:
        content = f.readlines()
    content = [x.strip() for x in content]

    def traverse_counterexample(fname,gwg,partitionGrid,beliefcons,ind,agentstate_parent):
        global visited
        global toRefine
        global truebeliefstates

        visited.add(ind)          

        beliefLeaf = set()
        
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
        envstate = int(''.join(str(e) for e in envstatebin)[::-1],2)
        
        if envstate < len(xstates):
            print 'Environment position is ', xstates[envstate]
            truebeliefstates = {xstates[envstate]}
        else:
            for b in beliefcombs[envstate - len(xstates)]:
                beliefstate = beliefstate.union(partitionGrid[b])
            print 'Environment position is ', beliefstate
            truebeliefstates_next = set()
            for s in truebeliefstates:
                for a in gwg.actlist:
                    for t in np.nonzero(gwg.prob[a][s])[0]:
                        truebeliefstates_next.add(t)
            truebeliefstates_next = truebeliefstates_next - set(gwg.obstacles)
            truebeliefstates = copy.deepcopy(truebeliefstates_next)
            
        if len(agentstatebin) > 0:
            agentstate = xstates[int(''.join(str(e) for e in agentstatebin)[::-1], 2)]
            print 'Agent position is ', agentstate
        else: # failure state
            return (False,set())
        if content[ind+1] == 'With no successors.': # terminal state
            return (False,set())
        
        if len(beliefstate) > 0:
            visstates = set(gwg.states) - visibility.invis(gwg,agentstate_parent) - set(gwg.walls)
            beliefinvisstates = beliefstate - visstates.intersection(beliefstate)
            truebeliefwithvis = copy.deepcopy(truebeliefstates)
            truebeliefstates = truebeliefstates.intersection(beliefinvisstates)
            
            if len(beliefinvisstates) > beliefcons:
                if len(truebeliefstates) <= beliefcons:
                    print 'Invisible states in belief states are ', beliefinvisstates
                    print "Fully refined belief states are", truebeliefstates
                    print "Size of abstract belief set exceeds the threshold."
                    print "Size of conctrete belief set meets thethreshold."
                    
                    # partitions in the leaf node that wull be refined
                    tr = set()
                    for b in beliefcombs[envstate - len(xstates)]:
                        tr.add(b)
                    toRefine.append(tr)
                    
                    beliefLeaf = copy.deepcopy(truebeliefwithvis)
                    return (True,beliefLeaf)
                else:
                    return (False,set())     
        '''
        recurse over the successors (subtrees) of the current node, searching for a leaf node to refine
        if in some subtree such node is found, add the current node to the counterexample and return 
        '''
        truebeliefstates_current = copy.deepcopy(truebeliefstates)
        nextposstates = map(int,content[ind+1][18:].split(', '))
        for succ in range(0,len(content),2):
            if (int(content[succ].split(' ')[1]) in nextposstates):
                if (succ not in visited):
                    truebeliefstates = copy.deepcopy(truebeliefstates_current)
                    (res,leafBelief) = traverse_counterexample(fname,gwg,partitionGrid,beliefcons,succ,agentstate)
                    if res:
                        tr = set()
                        if envstate >= len(xstates):
                            for b in beliefcombs[envstate - len(xstates)]:
                                tr.add(b)
                        toRefine.append(tr)
                        return (res,leafBelief)
        return (False,set())
        
    (res,leafBelief) = traverse_counterexample(fname,gwg,partitionGrid,beliefcons,0,gwg.current)
    
    return (res,leafBelief,toRefine)
    
