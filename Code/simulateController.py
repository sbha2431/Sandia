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

def parseJson(filename):
    automaton = dict()
    file = open(filename)
    data = json.load(file)
    file.close()
    variables = dict()
    for var in data['variables']:
        if '@' in var:
            v = var[0:var.index('@')]
            Flag = True
        else:
            v = copy.deepcopy(var)
            Flag = False
        if v not in variables.keys():
            if Flag:
                variables[v] = [data['variables'].index(var), max(loc for loc, val in enumerate(data['variables']) if val[0:val.index('@')] == v)+1]
            else:
                variables[v] = [data['variables'].index(var), data['variables'].index(var)+1]

    for s in data['nodes'].keys():
        automaton[int(s)] = dict.fromkeys(['State','Successors'])
        automaton[int(s)]['State'] = dict()
        automaton[int(s)]['Successors'] = []
        for v in variables.keys():
            bin = data['nodes'][s]['state'][variables[v][0]:variables[v][1]]
            automaton[int(s)]['State'][v] = int(''.join(str(e) for e in bin)[::-1], 2)
            automaton[int(s)]['Successors'] = data['nodes'][s]['trans']
    return automaton

def getGridstate(gwg,currstate,dirn):
    if dirn == 'W':
        return currstate - 1
    elif dirn == 'E':
        return currstate + 1
    elif dirn == 'S':
        return currstate + gwg.ncols
    elif dirn == 'N':
        return currstate - gwg.ncols


def userControlled_partition(filename,gwg,partitionGrid,moveobstacles,invisibilityset):
    automaton = parseJson(filename)
    automaton_state = 0
    xstates = list(set(gwg.states))
    allstates = copy.deepcopy(xstates)
    beliefcombs = powerset(partitionGrid.keys())
    for i in range(gwg.nstates,gwg.nstates+ len(beliefcombs)):
        allstates.append(i)
    gwg.colorstates = [set(), set()]
    gridstate = copy.deepcopy(moveobstacles[0])
    while True:
        envstate = automaton[automaton_state]['State']['st']
        agentstate = automaton[automaton_state]['State']['s']
        print 'Agent state is ', agentstate
        gwg.render()
        gwg.moveobstacles[0] = copy.deepcopy(gridstate)

        gwg.render()
        gwg.current = [copy.deepcopy(agentstate)]

        gwg.colorstates[0] = set()
        gwg.colorstates[0].update(invisibilityset[agentstate])
        gwg.render()
        # gwg.draw_state_labels()
        
        nextstates = automaton[automaton_state]['Successors']
        nextstatedirn = {'W':None,'E':None,'S':None,'N':None,'Belief':set()}
        for n in nextstates:
            nenvstate = automaton[n]['State']['st']
            if nenvstate == gwg.moveobstacles[0] - 1:
                nextstatedirn['W'] = n
            if nenvstate == gwg.moveobstacles[0] + 1:
                nextstatedirn['E'] = n
            if nenvstate == gwg.moveobstacles[0] + gwg.ncols:
                nextstatedirn['S'] = n
            if nenvstate == gwg.moveobstacles[0] - gwg.ncols:
                nextstatedirn['N'] = n
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
                    if arrow == 'W':
                        gridstate = gwg.moveobstacles[0] - 1
                    elif arrow == 'E':
                        gridstate = gwg.moveobstacles[0] + 1
                    elif arrow == 'S':
                        gridstate = gwg.moveobstacles[0] + gwg.ncols
                    elif arrow == 'N':
                        gridstate = gwg.moveobstacles[0] - gwg.ncols
                    
                    for n in nextstatedirn['Belief']:
                        nenvstate = automaton[n]['State']['st']
                        nextbeliefs = beliefcombs[len(beliefcombs) - (len(allstates) - allstates.index(nenvstate))]
                        if any(gridstate in partitionGrid[x] for x in nextbeliefs):
                            nextstate = copy.deepcopy(n)
                            print 'Environment state in automaton is', allstates.index(nenvstate)
                            print 'Belief state is', beliefcombs[allstates.index(nenvstate) - len(xstates)]
                            nextagentstate = automaton[n]['State']['s']
                            invisstates = invisibilityset[nextagentstate]
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
                    nenvstate = automaton[nextstate]['State']['st']
                    print 'Environment state in automaton is', allstates.index(nenvstate)
                    print 'Environment state in grid is', nenvstate
                    gridstate = copy.deepcopy(nenvstate)
                    gwg.colorstates[1] = set()
                    gwg.render()


            if len(automaton[nextstate]['Successors']) > 0:
                break

        print 'Automaton state is ', nextstate
        automaton_state = copy.deepcopy(nextstate)

def userControlled_partition_dist(filename,gwg,partitionGrid,moveobstacles,allowed_states,invisibilityset):
    automaton = [None]*gwg.nagents
    automaton_state = [None]*gwg.nagents
    agentstate = [None]*gwg.nagents
    targetstate = [None]*gwg.nagents
    truebeliefstates = [set()]*gwg.nagents
    allstates = [[None]]*gwg.nagents
    beliefcombs = [[None]]*gwg.nagents
    xstates = list(set(gwg.states))
    for n in range(gwg.nagents):
        automaton[n] = parseJson(filename[n])
        automaton_state[n] = 0
        allstates[n] = copy.deepcopy(xstates)
        beliefcombs[n] = powerset(partitionGrid[n].keys())
        for i in range(gwg.nstates,gwg.nstates+ len(beliefcombs[n])):
            allstates[n].append(i)
        allstates[n].append(len(allstates[n])) # nominal state if target leaves allowed region
    gwg.colorstates = [set(), set()]
    gridstate = copy.deepcopy(moveobstacles[0])
    while True:
        gwg.colorstates[0] = set()
        for n in range(gwg.nagents):
            agentstate[n] = automaton[n][automaton_state[n]]['State']['s']
            targetstate[n] = automaton[n][automaton_state[n]]['State']['st']
            print 'Agent state is ', agentstate
            gwg.colorstates[0] = gwg.colorstates[0].union(invisibilityset[n][agentstate[n]])


        activeagents = set(range(gwg.nagents))
        for n in range(gwg.nagents):
            if targetstate[n] == allstates[n][-1]:
                activeagents.remove(n)

        gwg.render()
        gwg.moveobstacles[0] = copy.deepcopy(gridstate)

        gwg.render()
        gwg.current = copy.deepcopy(agentstate)

        gwg.render()
        # gwg.draw_state_labels()

        nextstatedirn = [dict()]*gwg.nagents
        nexttargetstate = [None]*gwg.nagents
        nextagentstate = [None]*gwg.nagents
        nextstate = [None]*gwg.nagents
        for m in activeagents:
            nextstatedirn[m] = {'W':None,'E':None,'S':None,'N':None,'R':None,'Belief':set(),'Out':None,'Incoming':set()}
            nextstates = automaton[m][automaton_state[m]]['Successors']
            for n in nextstates:
                nexttargetstate[m]= automaton[m][n]['State']['st']
                if nexttargetstate[m] == allstates[m][-1]:
                    nextstatedirn[m]['Out'] = n
                elif nexttargetstate[m] == gwg.moveobstacles[0] - 1:
                    nextstatedirn[m]['W'] = n
                elif nexttargetstate[m] == gwg.moveobstacles[0] + 1:
                    nextstatedirn[m]['E'] = n
                elif nexttargetstate[m] == gwg.moveobstacles[0] + gwg.ncols:
                    nextstatedirn[m]['S'] = n
                elif nexttargetstate[m] == gwg.moveobstacles[0] - gwg.ncols:
                    nextstatedirn[m]['N'] = n
                elif nexttargetstate[m] == gwg.moveobstacles[0]:
                    nextstatedirn[m]['R'] = n
                elif nexttargetstate[m] not in xstates:
                    nextstatedirn[m]['Belief'].add(n)

        for m in set(range(gwg.nagents)) - activeagents:
            nextstatedirn[m] = {'W':None,'E':None,'S':None,'N':None,'R':None,'Belief':set(),'Out':None,'Incoming':set()}
            nextstates = automaton[m][automaton_state[m]]['Successors']
            for n in nextstates:
                nexttargetstate[m]= automaton[m][n]['State']['st']
                if nexttargetstate[m] == allstates[m][-1]:
                    nextstatedirn[m]['Out'] = n
                elif nexttargetstate[m] in allowed_states[m]:
                    nextstatedirn[m]['Incoming'].add(n)

        while True:
            while None in nextstate:
                while True:
                    arrow = gwg.getkeyinput()
                    if arrow != None:
                        break
                for m in activeagents:
                    nextstate[m] = nextstatedirn[m][arrow]
                    if nextstate[m] == None:
                        gridstate = getGridstate(gwg,moveobstacles[0],arrow)
                        if gridstate in allowed_states[m]:
                            for n in nextstatedirn[m]['Belief']:
                                nexttargetstate[m] = automaton[m][n]['State']['st']
                                nextbeliefs = beliefcombs[m][len(beliefcombs[m]) - (len(allstates[m]) - allstates[m].index(nexttargetstate[m]))]
                                if any(gridstate in partitionGrid[m][x] for x in nextbeliefs):
                                    nextstate[m] = copy.deepcopy(n)
                                    print 'Environment state in automaton is', allstates[m].index(nexttargetstate[m])
                                    print 'Belief state is', beliefcombs[allstates[m].index(nexttargetstate[m]) - len(xstates)]
                                    nextagentstate[m] = automaton[m][n]['State']['s']
                                    invisstates = invisibilityset[m][nextagentstate[m]]
                                    visstates = set(xstates) - invisstates
                                    if nexttargetstate[m] not in xstates:
                                        beliefcombstate = beliefcombs[m][allstates[m].index(nexttargetstate[m]) - len(xstates)]
                                        beliefstates = set()
                                        for b in beliefcombstate:
                                            beliefstates = beliefstates.union(partitionGrid[m][b])
                                        truebeliefstates[m] = beliefstates - beliefstates.intersection(visstates)

                                        # print 'True belief set is ', truebeliefstates
                                        # print 'Size of true belief set is ', len(truebeliefstates)
                        else:
                            nextstate[m] = nextstatedirn[m]['Out']
                            nexttargetstate[m] = automaton[m][nextstate[m]]['State']['st']
                            print 'Environment state in automaton is', allstates[m].index(nexttargetstate[m])
                            print 'Environment state in grid is', nexttargetstate[m]
                            truebeliefstates[m] = set()
                            gwg.render()
                    else:
                        nexttargetstate[m] = automaton[m][nextstate[m]]['State']['st']
                        gridstate = copy.deepcopy(nexttargetstate[m])
                        print 'Environment state in automaton is', allstates[m].index(nexttargetstate[m])
                        print 'Environment state in grid is', nexttargetstate[m]
                        truebeliefstates[m] = set()
                        gwg.render()
                for m in set(range(gwg.nagents)) - activeagents:
                    if gridstate in allowed_states[m]:
                        for ns in nextstatedirn[m]['Incoming']:
                            if gridstate == automaton[m][ns]['State']['st']:
                                nextstate[m] = ns
                        nexttargetstate[m] = automaton[m][nextstate[m]]['State']['st']
                        print 'Environment state in automaton is', allstates[m].index(nexttargetstate[m])
                        print 'Environment state in grid is', nexttargetstate[m]
                        gwg.colorstates[1] = set()
                        gwg.render()
                        truebeliefstates[m] = set()
                    else:
                        nextstate[m] = nextstatedirn[m]['Out']
                        nexttargetstate[m] = automaton[m][nextstate[m]]['State']['st']
                        truebeliefstates[m] = set()

                gwg.colorstates[1] = set()
                for m in range(gwg.nagents):
                    gwg.colorstates[1] = gwg.colorstates[1].union(truebeliefstates[m])



            if len(automaton[0][nextstate[0]]['Successors']) > 0: #Fix this
                break

        print 'Automaton state is ', nextstate
        automaton_state = copy.deepcopy(nextstate)


def gazeboOutput(gwg,timestep):
    filename = 'statehistory15x20.txt'
    with open(filename,'a') as file:
        if timestep == 0:
            file.write('t,e,a\n')
        file.write('{},{},{}\n'.format(timestep,gwg.moveobstacles[0],gwg.current[0]))
        file.close()
