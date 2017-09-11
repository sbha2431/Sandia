__author__ = 'sudab'
import random
import simplejson as json
import time
import copy
import visibility
import grid_partition
import itertools


def powerset(s):
    x = len(s)
    a = []
    for i in range(1,1<<x):
        a.append({s[j] for j in range(x) if (i &(1<<j))})
    return a

def userControlled_belief_multitarget(filename,gwg,numbeliefstates):
    file = open(filename)
    data = json.load(file)
    file.close()
    xstates = list(set(gwg.states) - set(gwg.edges))
    partitionGrid = grid_partition.partitionGrid(gwg,numbeliefstates)
    allstates = copy.deepcopy(xstates)
    beliefcombs = powerset(partitionGrid.keys())
    for i in range(gwg.nstates,gwg.nstates+ len(beliefcombs)):
        allstates.append(i)
    targetletters = ['y','d','e','f','g']
    currstate = 0
    gridstate = copy.deepcopy(gwg.moveobstacles)
    gwg.colorstates = [set(), set()]
    while True:
        for v in data['variables']:
            if targetletters[0] not in v:
                envsize = data['variables'].index(v)
                break
        totstate = data['nodes'][str(currstate)]['state']
        envstate = [None]*len(gwg.moveobstacles)
        for targn in range(len(gwg.moveobstacles)):
            singleenvstatebin = totstate[envsize*targn:envsize*(targn+1)]
            envstate[targn] = allstates[int(''.join(str(e) for e in singleenvstatebin)[::-1],2)]
        agentstatebin = totstate[envsize*len(gwg.moveobstacles):len(totstate)]

        agentstate = [None]*gwg.nagents
        for n in range(gwg.nagents):
            singleagentstatebin = agentstatebin[n*len(agentstatebin)/gwg.nagents:(n+1)*len(agentstatebin)/gwg.nagents]
            agentstate[n] = xstates[int(''.join(str(e) for e in singleagentstatebin)[::-1], 2)]

        gwg.render()

        gwg.moveobstacles = copy.deepcopy(gridstate)

        gwg.render()
        gwg.current = copy.deepcopy(agentstate)
        print 'Agent state in grid is ', gwg.current[0]
        print 'Agent state in automaton is ', xstates.index(gwg.current[0])


        gwg.colorstates[0] = set()
        gwg.colorstates[0].update(visibility.invis(gwg,agentstate[0]))
        for n in range(1, gwg.nagents):
            gwg.colorstates[0] = gwg.colorstates.intersection(visibility.invis(gwg,agentstate[n]))
        # time.sleep(0.4)
        gwg.render()
        # gwg.draw_state_labels()
        dirns = ['Left','Right','Up','Down','Belief']
        nextdirns = list(itertools.product(dirns,repeat = len(gwg.moveobstacles)))
        nextstates = data['nodes'][str(currstate)]['trans']
        emptysets = [set() for x in range(len(nextdirns))]
        nextstatedirn = dict(zip(nextdirns,emptysets))
        for n in nextstates:
            targnextstatedirn = [None]*len(gwg.moveobstacles) # Where is each agent moving
            ntotstate = data['nodes'][str(n)]['state']
            nenvstate = [None]*len(gwg.moveobstacles)
            for targn in range(len(gwg.moveobstacles)):
                nsingleenvstatebin = ntotstate[envsize*targn:envsize*(targn+1)]
                nenvstate[targn] = allstates[int(''.join(str(e) for e in nsingleenvstatebin)[::-1],2)]
                if nenvstate[targn] == gwg.moveobstacles[targn] - 1:
                    targnextstatedirn[targn] = 'Left'
                elif nenvstate[targn] == gwg.moveobstacles[targn] + 1:
                    targnextstatedirn[targn] = 'Right'
                elif nenvstate[targn] == gwg.moveobstacles[targn] + gwg.ncols:
                    targnextstatedirn[targn] = 'Down'
                elif nenvstate[targn] == gwg.moveobstacles[targn] - gwg.ncols:
                    targnextstatedirn[targn] = 'Up'
                elif nenvstate[targn] not in xstates:
                    targnextstatedirn[targn] = 'Belief'
            if None not in targnextstatedirn:
                nextstatedirn[tuple(targnextstatedirn)].add(n)

        while True:
            nextstate = None
            combarrow = [None]*len(gwg.moveobstacles)
            while nextstate is None:
                for targn in range(len(gwg.moveobstacles)):
                    while True:
                        combarrow[targn] = gwg.getkeyinput()
                        if combarrow[targn] != None:
                            break
                nextstate = nextstatedirn[tuple(combarrow)]
                combdirn = [None]*len(gwg.moveobstacles)
                checker = 0
                if len(nextstate) == 0:
                    for targn in range(len(gwg.moveobstacles)):
                        arrow = combarrow[targn]
                        if arrow == 'Left':
                            gridstate[targn] = gwg.moveobstacles[targn] - 1
                        elif arrow == 'Right':
                            gridstate[targn] = gwg.moveobstacles[targn] + 1
                        elif arrow == 'Down':
                            gridstate[targn] = gwg.moveobstacles[targn] + gwg.ncols
                        elif arrow == 'Up':
                            gridstate[targn] = gwg.moveobstacles[targn] - gwg.ncols
                        if gridstate[targn] in visibility.invis(gwg,gwg.current[0]):
                            combdirn[targn] = 'Belief' # Means the particular target is in a belief state
                        else:
                            combdirn[targn] = arrow
                    for n in nextstatedirn[tuple(combdirn)]: #Need to figure out which target(s) are in belief states
                        ntotstate = data['nodes'][str(n)]['state']
                        nextbeliefs = set()
                        for targn in range(len(gwg.moveobstacles)):
                            nsingleenvstatebin = ntotstate[envsize*targn:envsize*(targn+1)]
                            nenvstate[targn] = allstates[int(''.join(str(e) for e in nsingleenvstatebin)[::-1],2)]
                            if nenvstate[targn] not in xstates:
                                nextbeliefs = nextbeliefs.union(beliefcombs[len(beliefcombs) - (len(allstates) - allstates.index(nenvstate[targn]))])

                        if any(gridstate[belieftargn] in partitionGrid[x] for x in nextbeliefs for belieftargn in [i for i, y in enumerate(combdirn) if y == 'Belief']):
                            for belieftargn in [i for i, x in enumerate(combdirn) if x == 'Belief']:
                                if envstate[belieftargn] in xstates or (beliefcombs[len(beliefcombs) - (len(allstates) - allstates.index(envstate[belieftargn]))] < nextbeliefs):
                                    checker = 1
                                    nextstate = copy.deepcopy(n)
                                    # print 'Environment state in automaton is', allstates.index(nenvstate)
                                    # print 'Environment state in grid is', nenvstate
                                    nagentstatebin = ntotstate[envsize*len(gwg.moveobstacles):len(ntotstate)]
                                    nextagentstate = [None]*gwg.nagents
                                    for agent in range(gwg.nagents):
                                        singleagentstatebin = nagentstatebin[agent*len(nagentstatebin)/gwg.nagents:(agent+1)*len(nagentstatebin)/gwg.nagents]
                                        nextagentstate[agent] = xstates[int(''.join(str(e) for e in singleagentstatebin)[::-1], 2)]
                                    invisstates = visibility.invis(gwg,nextagentstate[0])
                                    visstates = set(xstates) - invisstates
                                    if nenvstate[belieftargn] not in xstates:
                                        beliefcombstate = beliefcombs[allstates.index(nenvstate[belieftargn]) - len(xstates)]
                                        beliefstates = set()
                                        for b in beliefcombstate:
                                            beliefstates = beliefstates.union(partitionGrid[b])
                                        truebeliefstates = beliefstates - beliefstates.intersection(visstates)
                                        gwg.colorstates[1] = copy.deepcopy(truebeliefstates)
                                        gwg.render()
                                        print 'Belief set is ', truebeliefstates
                                        print 'Size of belief set is ', len(truebeliefstates)
                                elif checker == 0 and beliefcombs[len(beliefcombs) - (len(allstates) - allstates.index(envstate[belieftargn]))] <= nextbeliefs:
                                    nextstate = copy.deepcopy(n)
                                    # print 'Environment state in automaton is', allstates.index(nenvstate)
                                    # print 'Environment state in grid is', nenvstate
                                    nagentstatebin = ntotstate[envsize*len(gwg.moveobstacles):len(ntotstate)]
                                    nextagentstate = [None]*gwg.nagents
                                    for agent in range(gwg.nagents):
                                        singleagentstatebin = nagentstatebin[agent*len(nagentstatebin)/gwg.nagents:(agent+1)*len(nagentstatebin)/gwg.nagents]
                                        nextagentstate[agent] = xstates[int(''.join(str(e) for e in singleagentstatebin)[::-1], 2)]
                                    invisstates = visibility.invis(gwg,nextagentstate[0])
                                    visstates = set(xstates) - invisstates
                                    if nenvstate not in xstates:
                                        beliefcombstate = beliefcombs[allstates.index(nenvstate[belieftargn]) - len(xstates)]
                                        beliefstates = set()
                                        for b in beliefcombstate:
                                            beliefstates = beliefstates.union(partitionGrid[b])
                                        truebeliefstates = beliefstates - beliefstates.intersection(visstates)
                                        gwg.colorstates[1] = copy.deepcopy(truebeliefstates)
                                        # gwg.render()
                                        print 'Belief set is ', truebeliefstates
                                        print 'Size of belief set is ', len(truebeliefstates)

                else:
                    (nextstate,) =  nextstate
                    ntotstate = data['nodes'][str(nextstate)]['state']
                    for targn in range(len(gwg.moveobstacles)):
                        nsingleenvstatebin = ntotstate[envsize*targn:envsize*(targn+1)]
                        nenvstate[targn] = xstates[int(''.join(str(e) for e in nsingleenvstatebin)[::-1],2)]
                    # print 'Environment state in automaton is', allstates.index(nenvstate)
                    # print 'Environment state in grid is', nenvstate
                    gridstate = copy.deepcopy(nenvstate)
                    gwg.colorstates[1] = set()
                    gwg.render()


            if len(data['nodes'][str(nextstate)]['trans']) > 0:
                break

        print 'Automaton state is ', nextstate
        currstate = nextstate

def userControlled_partition(filename,gwg,partitionGrid,moveobstacles):
    file = open(filename)
    data = json.load(file)
    file.close()
    xstates = list(set(gwg.states) - set(gwg.edges))
    allstates = copy.deepcopy(xstates)
    beliefcombs = powerset(partitionGrid.keys())
    for i in range(gwg.nstates,gwg.nstates+ len(beliefcombs)):
        allstates.append(i)

    gwg.moveobstacles = copy.deepcopy(moveobstacles)
    currstate = 0
    gridstate = copy.deepcopy(moveobstacles[0])
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
        gwg.render()
        # gwg.draw_state_labels()
        
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
                        nextbeliefs = beliefcombs[len(beliefcombs) - (len(allstates) - allstates.index(nenvstate))]
                        if any(gridstate in partitionGrid[x] for x in nextbeliefs):
                            nextstate = copy.deepcopy(n)
                            print 'Environment state in automaton is', allstates.index(nenvstate)
                            print 'Belief state is', beliefcombs[allstates.index(nenvstate) - len(xstates)]
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
                                print 'True belief set is ', truebeliefstates
                                print 'Size of true belief set is ', len(truebeliefstates)
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

def gazeboOutput(gwg,timestep):
    filename = 'statehistory15x20.txt'
    with open(filename,'a') as file:
        if timestep == 0:
            file.write('t,e,a\n')
        file.write('{},{},{}\n'.format(timestep,gwg.moveobstacles[0],gwg.current[0]))
        file.close()
