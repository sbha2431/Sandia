__author__ = 'sudab'

import copy
import grid_partition
import visibility

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

    while True:
        envstatebin = []
        agentstatebin = []
        beliefstate = set()
        for r in range(len(content[ind])):
            if content[ind][r] == 'y':
                if content[ind][r+2] == '0':
                    envstatebin.append(content[ind][r+9])
                else:
                    envstatebin.append(content[ind][r+4])
            elif content[ind][r] == 'x':
                if content[ind][r+2] == '0':
                    agentstatebin.append(content[ind][r+9])
                else:
                    agentstatebin.append(content[ind][r+4])
        envstate = int(''.join(str(e) for e in envstatebin)[::-1],2)
        if envstate < len(xstates):
            print 'Environment position is ', xstates[envstate]
        else:
            for b in beliefcombs[envstate - len(xstates)]:
                beliefstate = beliefstate.union(partitionGrid[b])
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
            print('There are a total of {} invisible belief states'.format(len(beliefinvisstates)))
            print 'Invisible states in belief states are ', beliefinvisstates
            gwg.moveobstacles = []
        else:
            gwg.moveobstacles[0] = copy.deepcopy(xstates[envstate])


        gwg.render()
        gwg.current[0] = copy.deepcopy(agentstate)

        gwg.colorstates = set()
        gwg.colorstates.update(visibility.invis(gwg,agentstate))
        gwg.colorstates = gwg.colorstates.intersection(visibility.invis(gwg,agentstate))
        gwg.render()
        gwg.draw_state_labels()


        nextposstates = map(int,content[ind+1][18:].split(', '))
        print 'Choose from one of the following states:', nextposstates
        nextautostate = int(raw_input('Next state in automaton: '))


        for w in range(0,len(content),2):
            if int(content[w].split(' ')[1]) == nextautostate:
                ind = w
                break



if __name__ == '__main__':
    from gridworld import Gridworld

    nrows = 8
    ncols = 7
    nagents = 1
    initial = [38]
    targets = [[ncols+1]]
    obstacles = [22,23,29,30,36,37,25,26,32,33,39,40,43,44,46,47]
    moveobstacles = [24]


    regionkeys = {'pavement','gravel','grass','sand','deterministic'}
    regions = dict.fromkeys(regionkeys,{-1})
    regions['deterministic']= range(nrows*ncols)

    gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
    gwg.render()
    gwg.draw_state_labels()
    beliefparts = 2
    beliefcons = 2
    fname = 'counterexample_small.txt'
    run_counterexample('counterexample_small.txt',gwg,beliefparts)
