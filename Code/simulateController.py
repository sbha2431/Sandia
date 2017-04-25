__author__ = 'sudab'
import random
import simplejson as json
import time
import copy
import visibility
import grid_partition


def powerset(s):
    x = len(s)
    a = []
    for i in range(1,1<<x):
        a.append({s[j] for j in range(x) if (i &(1<<j))})
    return a


def randomControlled(filename,gwg): # No longer supported
    file = open(filename)
    data = json.load(file)
    file.close()
    xstates = list(set(gwg.states) - set(gwg.edges))
    currstate = 0
    while gwg.current not in gwg.targets:
        totstate = data['nodes'][str(currstate)]['state']
        envstatebin = totstate[0:len(totstate)/2]
        agentstatebin = totstate[len(totstate)/2:len(totstate)]
        envstate = xstates[int(''.join(str(e) for e in envstatebin)[::-1],2)]
        agentstate = xstates[int(''.join(str(e) for e in agentstatebin)[::-1],2)]
        gwg.moveobstacles[0] = envstate
        gwg.render()
        time.sleep(0.2)
        gwg.current = agentstate
        gwg.render()
        time.sleep(0.2)
        currstate = nextstate

        while True:
            nextstate = random.sample((data['nodes'][str(currstate)]['trans']), 1)[0]
            if len(data['nodes'][str(nextstate)]['trans']) > 0:
                break

def userControlled(filename,gwg):
    file = open(filename)
    data = json.load(file)
    file.close()
    xstates = list(set(gwg.states) - set(gwg.edges))
    currstate = 0
    while True:
        if gwg.getkeyinput() == 'q':
        # press 'q' to exit
            break
        totstate = data['nodes'][str(currstate)]['state']
        envstatebin = totstate[0:len(totstate)/(gwg.nagents+1)]
        agentstatebin = totstate[len(totstate)/(gwg.nagents+1):len(totstate)]
        envstate = xstates[int(''.join(str(e) for e in envstatebin)[::-1],2)]
        agentstate = [None]*gwg.nagents
        for n in range(gwg.nagents):
            singleagentstatebin = agentstatebin[n*len(agentstatebin)/gwg.nagents:(n+1)*len(agentstatebin)/gwg.nagents]
            agentstate[n] = xstates[int(''.join(str(e) for e in singleagentstatebin)[::-1], 2)]

        gwg.render()
        gwg.colorstates = set()
        gwg.colorstates.update(visibility.invis(gwg,agentstate[0]))
        for n in range(1, gwg.nagents):
            gwg.colorstates = gwg.colorstates.intersection(visibility.invis(gwg,agentstate[n]))
        gwg.moveobstacles[0] = copy.deepcopy(envstate)
        # time.sleep(1)
        gwg.current = copy.deepcopy(agentstate)
        gwg.render()
        # print xstates.index(envstate)
        # print xstates.index(agentstate)
        # print visibility.isVis(gwg,agentstate,envstate)
        # time.sleep(0.3)

        nextstates = data['nodes'][str(currstate)]['trans']
        nextstatedirn = {'Left':None,'Right':None,'Down':None,'Up':None}
        for n in nextstates:
            ntotstate = data['nodes'][str(n)]['state']
            nenvstatebin = ntotstate[0:len(ntotstate)/(gwg.nagents+1)]
            nenvstate = xstates[int(''.join(str(e) for e in nenvstatebin)[::-1],2)]
            if nenvstate == gwg.moveobstacles[0] - 1:
                nextstatedirn['Left'] = n
            if nenvstate == gwg.moveobstacles[0] + 1:
                nextstatedirn['Right'] = n
            if nenvstate == gwg.moveobstacles[0] + gwg.ncols:
                nextstatedirn['Down'] = n
            if nenvstate == gwg.moveobstacles[0] - gwg.ncols:
                nextstatedirn['Up'] = n
        while True:
            while True:
                arrow = gwg.getkeyinput()
                if arrow != None:
                    break
            nextstate = nextstatedirn[arrow]
            if len(data['nodes'][str(nextstate)]['trans']) > 0:
                break
        currstate = nextstate


def userControlled_belief(filename,gwg,numbeliefstates):
    file = open(filename)
    data = json.load(file)
    file.close()
    xstates = list(set(gwg.states) - set(gwg.edges))
    partitionGrid = grid_partition.partitionGrid(gwg,numbeliefstates)
    allstates = copy.deepcopy(xstates)
    beliefcombs = powerset(partitionGrid.keys())
    for i in range(gwg.nstates,gwg.nstates+ len(beliefcombs)):
        allstates.append(i)

    currstate = 0
    gridstate = copy.deepcopy(gwg.moveobstacles[0])
    gwg.colorstates = [set(), set()]
    while True:
        for v in data['variables']:
            if 'y' not in v:
                envsize = data['variables'].index(v)
                break
        totstate = data['nodes'][str(currstate)]['state']
        envstatebin = totstate[0:envsize]
        agentstatebin = totstate[envsize:len(totstate)]
        envstate = allstates[int(''.join(str(e) for e in envstatebin)[::-1],2)]
        agentstate = [None]*gwg.nagents
        for n in range(gwg.nagents):
            singleagentstatebin = agentstatebin[n*len(agentstatebin)/gwg.nagents:(n+1)*len(agentstatebin)/gwg.nagents]
            agentstate[n] = xstates[int(''.join(str(e) for e in singleagentstatebin)[::-1], 2)]

        gwg.render()

        gwg.moveobstacles[0] = copy.deepcopy(gridstate)

        gwg.render()
        gwg.current = copy.deepcopy(agentstate)
        print 'Agent state in grid is ', gwg.current[0]
        print 'Agent state in automaton is ', xstates.index(gwg.current[0])


        gwg.colorstates[0] = set()
        gwg.colorstates[0].update(visibility.invis(gwg,agentstate[0]))
        for n in range(1, gwg.nagents):
            gwg.colorstates[0] = gwg.colorstates.intersection(visibility.invis(gwg,agentstate[n]))
        time.sleep(0.4)
        gwg.render()
        gwg.draw_state_labels()
        nextstates = data['nodes'][str(currstate)]['trans']
        nextstatedirn = {'Left':None,'Right':None,'Down':None,'Up':None,'Belief':set()}
        for n in nextstates:
            ntotstate = data['nodes'][str(n)]['state']
            nenvstatebin = ntotstate[0:envsize]
            nenvstate = allstates[int(''.join(str(e) for e in nenvstatebin)[::-1],2)]
            if nenvstate == gwg.moveobstacles[0] - 1:
                nextstatedirn['Left'] = n
            if nenvstate == gwg.moveobstacles[0] + 1:
                nextstatedirn['Right'] = n
            if nenvstate == gwg.moveobstacles[0] + gwg.ncols:
                nextstatedirn['Down'] = n
            if nenvstate == gwg.moveobstacles[0] - gwg.ncols:
                nextstatedirn['Up'] = n
            if nenvstate not in xstates:
                nextstatedirn['Belief'].add(n)
        while True:
            nextstate = None
            while nextstate == None:
                while True:
                    arrow = gwg.getkeyinput()
                    if arrow != None:
                        break
                nextstate = nextstatedirn[arrow]
                if nextstate == None:
                    if arrow == 'Left':
                        gridstate = gwg.moveobstacles[0] - 1
                    elif arrow == 'Right':
                        gridstate = gwg.moveobstacles[0] + 1
                    elif arrow == 'Down':
                        gridstate = gwg.moveobstacles[0] + gwg.ncols
                    elif arrow == 'Up':
                        gridstate = gwg.moveobstacles[0] - gwg.ncols
                    for n in nextstatedirn['Belief']:
                        ntotstate = data['nodes'][str(n)]['state']
                        nenvstatebin = ntotstate[0:envsize]
                        nenvstate = allstates[int(''.join(str(e) for e in nenvstatebin)[::-1],2)]

                        for beliefstate in beliefcombs[len(beliefcombs) - (len(allstates) - allstates.index(nenvstate))]:
                            if gridstate in partitionGrid[beliefstate]:
                                nextstate = copy.deepcopy(n)
                                print 'Environment state in automaton is', allstates.index(nenvstate)
                                print 'Environment state in grid is', nenvstate
                                nagentstatebin = ntotstate[envsize:len(ntotstate)]
                                nextagentstate = [None]*gwg.nagents
                                for n in range(gwg.nagents):
                                    singleagentstatebin = nagentstatebin[n*len(nagentstatebin)/gwg.nagents:(n+1)*len(nagentstatebin)/gwg.nagents]
                                    nextagentstate[n] = xstates[int(''.join(str(e) for e in singleagentstatebin)[::-1], 2)]
                                invisstates = visibility.invis(gwg,nextagentstate[0])
                                visstates = set(xstates) - invisstates
                                if nenvstate not in xstates:
                                    beliefcombstate = beliefcombs[allstates.index(nenvstate) - len(xstates)]
                                    beliefstates = set()
                                    for b in beliefcombstate:
                                        beliefstates = beliefstates.union(partitionGrid[b])
                                    truebeliefstates = beliefstates - beliefstates.intersection(visstates)
                                    gwg.colorstates[1] = copy.deepcopy(truebeliefstates)
                                    gwg.render()
                                    print 'Belief set is ', truebeliefstates
                                    print 'Size of belief set is ', len(truebeliefstates)
                else:
                    ntotstate = data['nodes'][str(nextstate)]['state']
                    nenvstatebin = ntotstate[0:envsize]
                    nenvstate = xstates[int(''.join(str(e) for e in nenvstatebin)[::-1],2)]
                    print 'Environment state in automaton is', allstates.index(nenvstate)
                    print 'Environment state in grid is', nenvstate
                    gridstate = copy.deepcopy(nenvstate)
                    gwg.colorstates[1] = set()
                    gwg.render()


            if len(data['nodes'][str(nextstate)]['trans']) > 0:
                break

        print 'Automaton state is ', nextstate
        currstate = nextstate

def simulate_path(gwg,filename, states):
    file = open(filename)
    data = json.load(file)
    file.close()
    xstates = list(set(gwg.states) - set(gwg.edges))
    for currstate in states:
        for v in data['variables']:
            if 'y' not in v:
                envsize = data['variables'].index(v)
                break
        totstate = data['nodes'][str(currstate)]['state']
        envstatebin = totstate[0:envsize]
        envstate = xstates[int(''.join(str(e) for e in envstatebin)[::-1],2)]
        agentstatebin = totstate[envsize:len(totstate)]
        agentstate = [None]*gwg.nagents
        for n in range(gwg.nagents):
            singleagentstatebin = agentstatebin[n*len(agentstatebin)/gwg.nagents:(n+1)*len(agentstatebin)/gwg.nagents]
            agentstate[n] = xstates[int(''.join(str(e) for e in singleagentstatebin)[::-1], 2)]

        gwg.render()

        gwg.moveobstacles[0] = copy.deepcopy(envstate)

        gwg.render()
        gwg.current = copy.deepcopy(agentstate)
        print 'Agent state in grid is ', gwg.current[0]
        print 'Agent state in automaton is ', xstates.index(gwg.current[0])


        gwg.colorstates = set()
        gwg.colorstates.update(visibility.invis(gwg,agentstate[0]))
        for n in range(1, gwg.nagents):
            gwg.colorstates = gwg.colorstates.intersection(visibility.invis(gwg,agentstate[n]))
        time.sleep(0.4)
        gwg.render()
        gwg.draw_state_labels()

if __name__ == '__main__':
    from gridworld import Gridworld
    nrows = 15
    ncols = 20
    nagents = 1
    initial = [237]
    targets = [[ncols+1],[ncols*2+1]]
    obsnum = 3
    # obstacles = [27,63,78,26,37,36,72,62,73,77,67,66,76,52,53,68,16,17]
    obstacles = [153,154,155,173,174,175,193,194,195,213,214,215,233,234,235,68,69,88,89,108,109,128,129,183,184,185,186,187,203,204,205,206,207,223,224,225,226,227]
    # obstacles = [15,16,19]
    moveobstacles = [197]
    regionkeys = {'pavement','gravel','grass','sand','deterministic'}
    regions = dict.fromkeys(regionkeys,{-1})
    regions['deterministic']= range(nrows*ncols)

    gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
    gwg.render()
    filename = 'slugs_output.json'
    userControlled(filename,gwg)