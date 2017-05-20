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

visited = set()
truebeliefstates = set()
truebeliefstates_next = set()

def analyse_counterexample(fname,gwg,partitionGrid,beliefcons):
    global visited
    global truebeliefstates
    global truebeliefstates_next
    visited = set()
    truebeliefstates = set()
    truebeliefstates_next = set()

    def traverse_counterexample(fname,gwg,partitionGrid,beliefcons,ind):
        xstates = list(set(gwg.states) - set(gwg.edges))
        allstates = copy.deepcopy(xstates)
        beliefcombs = counterexample_parser.powerset(partitionGrid.keys())
        for i in range(gwg.nstates,gwg.nstates+ len(beliefcombs)):
            allstates.append(i)
        with open(fname) as f:
            content = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        content = [x.strip() for x in content]
        gwg.colorstates = [set(), set()]
        global truebeliefstates
        global truebeliefstates_next
        refineLeaf = []
        beliefLeaf = set()
        
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
            truebeliefstates_next = {xstates[envstate]}
            # for a in gwg.actlist:
            #     for t in np.nonzero(gwg.prob[a][xstates[envstate]])[0]:
            #         truebeliefstates_next.add(t)
        else:
            for b in beliefcombs[envstate - len(xstates)]:
                beliefstate = beliefstate.union(partitionGrid[b])
            truebeliefstates = copy.deepcopy(truebeliefstates_next)

            for s in truebeliefstates_next:
                for a in gwg.actlist:
                    for t in np.nonzero(gwg.prob[a][s])[0]:
                        truebeliefstates.add(t)
            truebeliefstates = truebeliefstates - set(gwg.obstacles)
            truebeliefstates_next = copy.deepcopy(truebeliefstates)

            print 'Environment position is ', beliefstate
            
        if len(agentstatebin) > 0:
            agentstate = xstates[int(''.join(str(e) for e in agentstatebin)[::-1], 2)]
        else:
            #print 'Failure state reached'
            return (False,[],set())
        print 'Agent position is ', agentstate
        if content[ind+1] == 'With no successors.':
            #print 'Reached terminal state'
            return (False,[],set())
        
        if len(beliefstate) > 0:
            invisstates = visibility.invis(gwg,agentstate)
            visstates = set(gwg.states) - invisstates - set(gwg.walls)
            beliefvisstates = visstates.intersection(beliefstate)
            beliefinvisstates = beliefstate - beliefvisstates
            truebeliefstates_next = truebeliefstates_next.intersection(beliefinvisstates)
            truebeliefstates = copy.deepcopy(truebeliefstates_next)
            #print('There are a total of {} invisible belief states'.format(len(beliefinvisstates)))
            print 'Invisible states in belief states are ', beliefinvisstates
            print "Fully refined belief states are", truebeliefstates
            if len(beliefinvisstates) > beliefcons:
                print "Size of abstract belief set exceeds the threshold."
                if len(truebeliefstates) <= beliefcons:
                    print "Size of conctrete belief set meets thethreshold."
                    for b in beliefcombs[envstate - len(xstates)]:
                        refineLeaf.append(b)
                    beliefLeaf = truebeliefstates
                    return (True,refineLeaf,beliefLeaf)
                else:
                    return (False,[],set())     
            gwg.colorstates[1] = copy.deepcopy(beliefinvisstates)
            gwg.moveobstacles = []
        else:
            gwg.moveobstacles = [copy.deepcopy(xstates[envstate])]
            gwg.colorstates[1] = set()

        nextposstates = map(int,content[ind+1][18:].split(', '))
        
        truebeliefstates_old = truebeliefstates_next
        global visited
        for succ in range(0,len(content),2):
            if (int(content[succ].split(' ')[1]) in nextposstates):
                if (succ not in visited):
                    visited.add(succ)
                    truebeliefstates_next = truebeliefstates_old
                    (res,refineLeaf,leafBelief) = traverse_counterexample(fname,gwg,partitionGrid,beliefcons,succ)
                    if res:
                        return (res,refineLeaf,leafBelief)
        return (False,[],set())
    
    return traverse_counterexample(fname,gwg,partitionGrid,beliefcons,0)
    
    
