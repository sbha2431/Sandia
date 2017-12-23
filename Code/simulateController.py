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

def gazeboOutput(gwg,timestep):
    filename = 'statehistory15x20.txt'
    with open(filename,'a') as file:
        if timestep == 0:
            file.write('t,e,a\n')
        file.write('{},{},{}\n'.format(timestep,gwg.moveobstacles[0],gwg.current[0]))
        file.close()
