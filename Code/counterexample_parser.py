__author__ = 'sudab'

import copy
import grid_partition

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
            beliefstate = set()
            for b in beliefcombs[envstate - len(xstates)]:
                beliefstate = beliefstate.union(partitionGrid[b])
            print 'Environment position is ', beliefstate
        agentstate = xstates[int(''.join(str(e) for e in agentstatebin)[::-1], 2)]
        print 'Agent position is ', agentstate
        if content[ind+1] == 'With no successors.':
            print 'Reached terminal state'
            break
        nextposstates = map(int,content[ind+1][18:].split(', '))
        print nextposstates
        nextautostate = int(raw_input('Next state in automaton: '))
        # nextautostate = nextposstates.pop()
        for w in range(0,len(content),2):
            if int(content[w].split(' ')[1]) == nextautostate:
                ind = w
                break



if __name__ == '__main__':
    fname = 'counterexample.txt'
    with open(fname) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    ind = 0
    envsize = int(content[ind][34])
    agentsize = int(content[ind][89])
    envstatebin = []
    agentstatebin = []
    # print map(int,content[3][18:].split(', '))
    print content[12].split(' ')