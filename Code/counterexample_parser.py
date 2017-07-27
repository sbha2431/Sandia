__author__ = 'sudab'

import copy
import grid_partition
import visibility
import numpy as np

def powerset(s):
    x = len(s)
    a = []
    for i in range(1,1<<x):
        a.append({s[j] for j in range(x) if (i &(1<<j))})
    return a

def run_counterexample(fname,gwg,numbeliefstates):
    xstates = list(set(gwg.states) - set(gwg.edges))
    partitionGrid = grid_partition.partitionGrid(gwg,numbeliefstates)
    allstates = copy.deepcopy(xstates)
    beliefcombs = powerset(partitionGrid.keys())
    for i in range(gwg.nstates,gwg.nstates+ len(beliefcombs)):
        allstates.append(i)
    with open(fname) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    ind = 0
    gwg.colorstates = [set(), set()]
    truebeliefstates = set()
    truebeliefstates_next = set()

    while True:
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
            print 'Failure state reached'
            break
        print 'Agent position is ', agentstate
        if content[ind+1] == 'With no successors.':
            print 'Reached terminal state'
            break

        if len(beliefstate) > 0:
            invisstates = visibility.invis(gwg,agentstate)
            visstates = set(gwg.states) - invisstates - set(gwg.walls)
            beliefvisstates = visstates.intersection(beliefstate)
            beliefinvisstates = beliefstate - beliefvisstates
            truebeliefstates_next = truebeliefstates_next.intersection(beliefinvisstates)
            truebeliefstates = copy.deepcopy(truebeliefstates_next)
            print "Fully refined belief states are", truebeliefstates
            print('There are a total of {} invisible belief states'.format(len(beliefinvisstates)))
            print 'Invisible states in belief states are ', beliefinvisstates
            gwg.colorstates[1] = copy.deepcopy(beliefinvisstates)
            gwg.moveobstacles = []
        else:
            gwg.moveobstacles = [copy.deepcopy(xstates[envstate])]
            gwg.colorstates[1] = set()


        gwg.render()
        gwg.current[0] = copy.deepcopy(agentstate)

        gwg.colorstates[0] = set()
        gwg.colorstates[0].update(visibility.invis(gwg,agentstate))
        gwg.colorstates[0] = gwg.colorstates[0].intersection(visibility.invis(gwg,agentstate))
        gwg.render()
        gwg.draw_state_labels()


        nextposstates = map(int,content[ind+1][18:].split(', '))
        print 'Choose from one of the following states:', nextposstates
        nextautostate = int(raw_input('Next state in automaton: '))


        for w in range(0,len(content),2):
            if int(content[w].split(' ')[1]) == nextautostate:
                ind = w
                break
        

def run_counterexample_part(fname,gwg,partitionGrid):
    xstates = list(set(gwg.states) - set(gwg.edges))
    allstates = copy.deepcopy(xstates)
    beliefcombs = powerset(partitionGrid.keys())
    for i in range(gwg.nstates,gwg.nstates+ len(beliefcombs)):
        allstates.append(i)
    with open(fname) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    ind = 0
    gwg.colorstates = [set(), set()]
    truebeliefstates = set()
    truebeliefstates_next = set()
    agentstate_parent = gwg.current[0]
    while True:
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
            #truebeliefstates = copy.deepcopy(truebeliefstates_next)

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
            print 'Failure state reached'
            break
        print 'Agent position is ', agentstate
        if content[ind+1] == 'With no successors.':
            print 'Reached terminal state'
            break

        if len(beliefstate) > 0:
            invisstates = visibility.invis(gwg,agentstate_parent)
            visstates = set(gwg.states) - invisstates - set(gwg.walls)
            beliefvisstates = visstates.intersection(beliefstate)
            beliefinvisstates = beliefstate - beliefvisstates
            truebeliefstates_next = truebeliefstates_next.intersection(beliefinvisstates)
            truebeliefstates = copy.deepcopy(truebeliefstates_next)
            print "Fully refined belief states are", truebeliefstates
            print('There are a total of {} invisible belief states'.format(len(beliefinvisstates)))
            print 'Invisible states in belief states are ', beliefinvisstates
            gwg.colorstates[1] = copy.deepcopy(beliefinvisstates)
            gwg.moveobstacles = []
        else:
            gwg.moveobstacles = [copy.deepcopy(xstates[envstate])]
            gwg.colorstates[1] = set()


        gwg.render()
        gwg.current[0] = copy.deepcopy(agentstate)

        gwg.colorstates[0] = set()
        gwg.colorstates[0].update(visibility.invis(gwg,agentstate_parent))
        gwg.colorstates[0] = gwg.colorstates[0].intersection(visibility.invis(gwg,agentstate_parent))
        gwg.render()
        gwg.draw_state_labels()


        nextposstates = map(int,content[ind+1][18:].split(', '))
        print 'Choose from one of the following states:', nextposstates
        nextautostate = int(raw_input('Next state in automaton: '))


        for w in range(0,len(content),2):
            if int(content[w].split(' ')[1]) == nextautostate:
                ind = w
                break

        agentstate_parent = copy.deepcopy(agentstate)        

        
if __name__ == '__main__':
    from gridworld import Gridworld

    nrows = 10
    ncols = 10
    nagents = 1
    initial = [88]
    targets = [[ncols+1]]
    obstacles = [34,44,45,54,55,64,47]
    moveobstacles = [68]

    regionkeys = {'pavement','gravel','grass','sand','deterministic'}
    regions = dict.fromkeys(regionkeys,{-1})
    regions['deterministic']= range(nrows*ncols)

    gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
    gwg.render()
    gwg.draw_state_labels()
    beliefparts = 4
    beliefcons = 10
    fname = 'counterexample.txt'
    run_counterexample('counterexample.txt',gwg,beliefparts)
