__author__ = 'sudab'

import numpy as np
import visibility
import grid_partition
import copy

def reach_states(gw,states):
    t =set()
    for state in states:
        for action in gw.actlist:
            t.update(set(np.nonzero(gw.prob[action][state])[0]))
    return t

def powerset(s):
    x = len(s)
    a = []
    for i in range(1,1<<x):
        a.append({s[j] for j in range(x) if (i &(1<<j))})
    return a

def write_to_slugs(gw,inittarg,vel=1):
    # agentstates = list(set(gw.states)- set(gw.edges))
    # agenttrans = set()
    # for s in set(gw.states) - set(gw.walls):
    #     for a in range(gw.nactions):
    #         for t in np.nonzero(gw.prob[gw.actlist[a]][s])[0]:
    #             agenttrans.add((agentstates.index(s),a,agentstates.index(t)))
    xstates = list(set(gw.states) - set(gw.edges))

    invisibilityset = [dict.fromkeys(set(gw.states) - set(gw.edges),frozenset({gw.nrows*gw.ncols+1}))]*gw.nagents
    for n in range(gw.nagents):
        for s in set(gw.states) - set(gw.edges):
            invisibilityset[n][s] = visibility.invis(gw,s) - set(gw.targets[n])
            if s in gw.obstacles:
                invisibilityset[n][s] = {-1}
    filename = 'slugs_input_'+str(gw.nagents)+'agents.structuredslugs'
    file = open(filename,'w')
    file.write('[INPUT]\n')
    file.write('y:0...{}\n'.format(len(xstates)))
    file.write('[OUTPUT]\n')
    agentletters = ['x','z','a','b','c']
    for n in range(gw.nagents):
        file.write(agentletters[n]+':0...{}\n'.format(len(xstates)))

    file.write('[ENV_INIT]\n')
    file.write('y = {}\n'.format(xstates.index(inittarg)))
    file.write('[SYS_INIT]\n')
    for n in range(gw.nagents):
        file.write(agentletters[n]+' = {}\n'.format(xstates.index(gw.current[n])))

    # writing env_trans
    file.write('\n[ENV_TRANS]\n')
    for x in range(len(xstates)):
        s = xstates[x]
        stri = "y = {} -> ".format(x)
        counter = 1
        for a in range(gw.nactions):
            for t in np.nonzero(gw.prob[gw.actlist[a]][s])[0]:
                if counter == 1:
                    stri += ' y\' = {}'.format(xstates.index(t))
                    counter += 1
                else:
                    stri += ' \\/ y\' = {} '.format(xstates.index(t))
                    counter += 1
        if counter > 1:
            stri += '\n'
            file.write(stri)
        for n in range(gw.nagents):
            file.write("{} = {} -> !y' = {}\n".format(agentletters[n],x,x))
    # Writing env_safety
    for obs in gw.obstacles:
        file.write('!y = {}\n'.format(xstates.index(obs)))

    for n in range(gw.nagents):
        file.write('!y = {}\n'.format(agentletters[n]))
        file.write('!y = {}\n'.format(xstates.index(gw.targets[n][0])))

    # writing sys_trans
    file.write('\n[SYS_TRANS]\n')
    for n in range(gw.nagents):
        for x in range(len(xstates)):
            s = xstates[x]
            stri = "{} = {} -> ".format(agentletters[n], x)
            t = reach_states(gw,{s})
            for i in range(1,vel):
                t.update(reach_states(gw,t))
            for t2 in t:
                stri += ' {}\' = {} \\/ '.format(agentletters[n], xstates.index(t2))
            stri = stri[:-3]
            stri += '\n'
            file.write(stri)
        # Writing sys_safety
        for obs in gw.obstacles:
            file.write('!{} = {}\n'.format(agentletters[n],xstates.index(obs)))

    for s in xstates:
        stri = 'y = {} -> '.format(xstates.index(s))
        for n in range(gw.nagents):
            stri += '(!{} = {}) /\\ '.format(agentletters[n], xstates.index(s))
        if s not in gw.obstacles:
            stri += '('
            for n in range(gw.nagents):
                invisstates = invisibilityset[n][s]
                if len(invisstates) > 1:
                    stri += '('
                    for x in invisstates:
                        stri += '!{} = {} /\\ '.format(agentletters[n],xstates.index(x))
                    stri = stri[:-3]
                    stri += ') \\/ '
            stri = stri[:-3]
            stri += ')'
        else:
            stri = stri[:-3]
        stri += '\n'
        file.write(stri)

    for s in xstates:
        for n in range(gw.nagents):
            stri = '{} = {} ->'.format(agentletters[n],xstates.index(s))
            for m in range(gw.nagents):
                if m!= n:
                    stri += ' !{} = {} /\\'.format(agentletters[m],xstates.index(s))
            stri = stri[:-2]
            stri += '\n'
            file.write(stri)

    # Writing sys_liveness
    file.write('\n[SYS_LIVENESS]\n')
    for n in range(gw.nagents):
        file.write('{} = {}\n'.format(agentletters[n],xstates.index(gw.targets[n][0])))

    # Writing env_liveness
    file.write('\n[ENV_LIVENESS]\n')
    # file.write('y = {}\n'.format(xstates.index(gw.current)))
    # file.write('y = {}\n'.format(xstates.index(inittarg)))
    # file.write('y = {}\n'.format(xstates.index(88)))
    file.write('y = {}\n'.format(xstates.index(gw.ncols+2)))
    file.close()

def write_to_slugs_belief(infile,gw,inittarg,vel=1,belief_partitions=0,beliefconstraint = 1):
    nonbeliefstates = list(set(gw.states) - set(gw.edges))
    partitionGrid = grid_partition.partitionGrid(gw,belief_partitions)
    allstates = copy.deepcopy(nonbeliefstates)
    beliefcombs = powerset(partitionGrid.keys())
    for i in range(gw.nstates,gw.nstates + len(beliefcombs)):
        allstates.append(i)

    invisibilityset = [dict.fromkeys(set(gw.states) - set(gw.edges),frozenset({gw.nrows*gw.ncols+1}))]*gw.nagents
    for n in range(gw.nagents):
        for s in set(gw.states) - set(gw.edges):
            invisibilityset[n][s] = visibility.invis(gw,s) - set(gw.targets[n])
            if s in gw.obstacles:
                invisibilityset[n][s] = {-1}
    filename = infile+'.structuredslugs'
    file = open(filename,'w')
    file.write('[INPUT]\n')
    file.write('y:0...{}\n'.format(len(allstates) - 1))
    file.write('[OUTPUT]\n')
    agentletters = ['x','z','a','b','c']
    for n in range(gw.nagents):
        file.write(agentletters[n]+':0...{}\n'.format(len(nonbeliefstates)-1))

    file.write('[ENV_INIT]\n')
    file.write('y = {}\n'.format(allstates.index(inittarg)))
    file.write('[SYS_INIT]\n')
    for n in range(gw.nagents):
        file.write(agentletters[n]+' = {}\n'.format(nonbeliefstates.index(gw.current[n])))

    # writing env_trans
    file.write('\n[ENV_TRANS]\n')
    for y in range(len(allstates)):
        if allstates[y] in nonbeliefstates:
            for x in range(len(nonbeliefstates)):
                sagent = nonbeliefstates[x]
                stri = " (x = {} /\\ y = {}) -> ".format(x,y)
                senv = allstates[y]
                beliefset = set()
                for a in range(gw.nactions):
                    for t in np.nonzero(gw.prob[gw.actlist[a]][senv])[0]:
                        if not any(t in invisibilityset[n][sagent] for n in range(gw.nagents)):
                            stri += ' y\' = {} \\/'.format(allstates.index(t))
                        else:
                            t2 = partitionGrid.keys()[[inv for inv in range(len(partitionGrid.values())) if t in partitionGrid.values()[inv]][0]]
                            beliefset.add(t2)
                if len(beliefset) > 0:
                    b2 = allstates[len(nonbeliefstates) + beliefcombs.index(beliefset)]
                    stri += ' y\' = {} \\/'.format(allstates.index(b2))
                stri = stri[:-3]
                stri += '\n'
                file.write(stri)
                for n in range(gw.nagents):
                    file.write("{} = {} -> !y' = {}\n".format(agentletters[n],x,allstates.index(sagent)))

        else:
            for x in range(len(nonbeliefstates)):
                sagent = nonbeliefstates[x]
                invisstates = invisibilityset[0][sagent]
                beliefcombstate = beliefcombs[y - len(nonbeliefstates)]
                beliefstates = set()
                visstates = set(nonbeliefstates) - invisstates
                for currbeliefstate in beliefcombstate:
                    beliefstates = beliefstates.union(partitionGrid[currbeliefstate])
                truebeliefstates = beliefstates - beliefstates.intersection(visstates)
                if len(truebeliefstates) > 0 or 1==1:
                    stri = " (x = {} /\\ y = {}) -> ".format(x,y)
                    for b in beliefstates:
                        beliefset = set()
                        for a in range(gw.nactions):
                            for t in np.nonzero(gw.prob[gw.actlist[a]][b])[0]:
                                if not any(t in invisibilityset[n][sagent] for n in range(gw.nagents)):
                                    stri += ' y\' = {} \\/'.format(allstates.index(t))
                                else:
                                    t2 = partitionGrid.keys()[[inv for inv in range(len(partitionGrid.values())) if t in partitionGrid.values()[inv]][0]]
                                    beliefset.add(t2)
                        if len(beliefset) > 0:
                            b2 = allstates[len(nonbeliefstates) + beliefcombs.index(beliefset)]
                            stri += ' y\' = {} \\/'.format(allstates.index(b2))
                    stri = stri[:-3]
                    stri += '\n'
                    file.write(stri)


    # Writing env_safety
    for obs in gw.obstacles:
        file.write('!y = {}\n'.format(allstates.index(obs)))

    for n in range(gw.nagents):
        # file.write('!y = {}\n'.format(agentletters[n]))
        file.write('!y = {}\n'.format(allstates.index(gw.targets[n][0])))

    # writing sys_trans
    file.write('\n[SYS_TRANS]\n')
    for n in range(gw.nagents):
        for x in range(len(nonbeliefstates)):
            s = nonbeliefstates[x]
            stri = "{} = {} -> ".format(agentletters[n], x)
            t = reach_states(gw,{s})
            for i in range(1,vel):
                t.update(reach_states(gw,t))
            for t2 in t:
                stri += ' {}\' = {} \\/ '.format(agentletters[n], nonbeliefstates.index(t2))
            stri = stri[:-3]
            stri += '\n'
            file.write(stri)
    # Writing sys_safety
        for obs in gw.obstacles:
            file.write('!{} = {}\n'.format(agentletters[n],nonbeliefstates.index(obs)))

    for s in set(nonbeliefstates):
        for n in range(gw.nagents):
            stri = 'y = {} -> !{} = {}\n'.format(allstates.index(s),agentletters[n],nonbeliefstates.index(s))
            file.write(stri)
            stri = 'y = {} -> !{}\' = {}\n'.format(allstates.index(s),agentletters[n],nonbeliefstates.index(s))
            file.write(stri)

    for b in beliefcombs:
        beliefset = set()
        for beliefstate in b:
            beliefset = beliefset.union(partitionGrid[beliefstate])
        if len(beliefset) > beliefconstraint:
            stri = 'y = {} -> '.format(len(nonbeliefstates)+beliefcombs.index(b))
            counter = 0
            stri += '('
            for n in range(gw.nagents):
                stri += '('
                for x in nonbeliefstates:
                    invisstates = invisibilityset[n][x]
                    visstates = set(nonbeliefstates) - invisstates
                    truebelief = beliefset - beliefset.intersection(visstates)
                    if len(truebelief) > beliefconstraint:
                        stri += '!{} = {} /\\ '.format(agentletters[n],nonbeliefstates.index(x))
                        counter += 1
                stri = stri[:-3]
                stri += ') \\/ '
            stri = stri[:-3]
            stri += ')'
            stri += '\n'
            if counter > 0:
                file.write(stri)

    if gw.nagents > 1:
        for s in nonbeliefstates:
            for n in range(gw.nagents):
                stri = '{} = {} ->'.format(agentletters[n],nonbeliefstates.index(s))
                for m in range(gw.nagents):
                    if m!= n:
                        stri += ' !{} = {} /\\'.format(agentletters[m],nonbeliefstates.index(s))
                stri = stri[:-2]
                stri += '\n'
                file.write(stri)

    # Writing sys_liveness
    file.write('\n[SYS_LIVENESS]\n')
    for n in range(gw.nagents):
        file.write('{} = {}\n'.format(agentletters[n],nonbeliefstates.index(gw.targets[n][0])))

    # Writing env_liveness
    file.write('\n[ENV_LIVENESS]\n')
    # file.write('y = {}\n'.format(xstates.index(gw.current)))
    # file.write('y = {}\n'.format(xstates.index(inittarg)))
    # file.write('y = {}\n'.format(xstates.index(88)))
    file.write('y = {}\n'.format(nonbeliefstates.index(gw.ncols+2)))
    file.close()