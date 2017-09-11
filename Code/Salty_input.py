__author__ = 'sudab'

import numpy as np
import visibility
import grid_partition
import copy
import itertools

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

def cartesian (lists):
    if lists == []: return [()]
    return [x + (y,) for x in cartesian(lists[:-1]) for y in lists[-1]]

def write_to_slugs_belief(infile,gw,vel=1,belief_partitions=0,beliefconstraint = 1):
    partitionGrid = grid_partition.partitionGrid(gw,belief_partitions)
    write_to_slugs_part(infile,gw,gw.moveobstacles[0],vel,partitionGrid, belief_constraint,0,True)
    

def write_to_slugs_part(infile,gw,inittarg,vel=1,partitionGrid =[], belief_safety = 0, belief_liveness = 0, target_reachability = False):
    
    nonbeliefstates = list(set(gw.states) - set(gw.edges))
    
    beliefcombs = powerset(partitionGrid.keys())
    
    allstates = copy.deepcopy(nonbeliefstates)
    for i in range(gw.nstates,gw.nstates + len(beliefcombs)):
        allstates.append(i)

    invisibilityset = [dict.fromkeys(set(gw.states) - set(gw.edges),frozenset({gw.nrows*gw.ncols+1}))]*gw.nagents
    for n in range(gw.nagents):
        for s in set(gw.states) - set(gw.edges):
            invisibilityset[n][s] = visibility.invis(gw,s) 
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
    file.write('y = {}\n'.format(allstates.index(gw.moveobstacles[0])))
    
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
                            if not t == sagent and t not in gw.targets[0]: # not allowed to move on agent's position
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
                visstates = set(nonbeliefstates) - invisstates
                
                beliefcombstate = beliefcombs[y - len(nonbeliefstates)]
                beliefstates = set()
                for currbeliefstate in beliefcombstate:
                    beliefstates = beliefstates.union(partitionGrid[currbeliefstate])
                for n in range(gw.nagents): # remove taret positions (no transitions from target positions)
                    beliefstates = beliefstates - set(gw.targets[n])
                beliefstates_vis = beliefstates.intersection(visstates)
                beliefstates_invis = beliefstates - beliefstates_vis
                
                if belief_safety > 0 and len(beliefstates_invis) > belief_safety:
                    continue # no transitions from error states
                
                if len(beliefstates) > 0:
                    stri = " (x = {} /\\ y = {}) -> ".format(x,y)
                    
                    beliefset = set()
                    for b in beliefstates: 
                        for a in range(gw.nactions):
                            for t in np.nonzero(gw.prob[gw.actlist[a]][b])[0]:
                                if not any(t in invisibilityset[n][sagent] for n in range(gw.nagents)):
                                    stri += ' y\' = {} \\/'.format(allstates.index(t))
                                else:
                                    if t in gw.targets[0]:
                                        continue
                                    t2 = partitionGrid.keys()[[inv for inv in range(len(partitionGrid.values())) if t in partitionGrid.values()[inv]][0]]
                                    beliefset.add(t2)
                    if len(beliefset) > 0:
                        b2 = allstates[len(nonbeliefstates) + beliefcombs.index(beliefset)]
                        stri += ' y\' = {} \\/'.format(allstates.index(b2))
                        
                    '''    
                    for b in beliefstates_vis: # successors of visible states in beliefstates
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
                    '''
                                               
                    stri = stri[:-3]
                    stri += '\n'
                    file.write(stri)


    # Writing env_safety
    for obs in gw.obstacles:
        file.write('!y = {}\n'.format(allstates.index(obs)))

    if target_reachability:
        for n in range(gw.nagents):
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
    
    if belief_safety > 0:
        for b in beliefcombs:
            beliefset = set()
            for beliefstate in b:
                beliefset = beliefset.union(partitionGrid[beliefstate])
            beliefset =  beliefset -set(gw.targets[0])
            if len(beliefset) > belief_safety:
                stri = 'y = {} -> '.format(len(nonbeliefstates)+beliefcombs.index(b))
                counter = 0
                stri += '('
                for n in range(gw.nagents):
                    stri += '('
                    for x in nonbeliefstates:
                        invisstates = invisibilityset[n][x]
                        beliefset_invis = beliefset.intersection(invisstates)
                        if len(beliefset_invis) > belief_safety:
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
    if target_reachability:
        for n in range(gw.nagents):
            file.write('{} = {}\n'.format(agentletters[n],nonbeliefstates.index(gw.targets[n][0])))

    stri  = ''
    if belief_liveness >0:
        for y in range(len(nonbeliefstates)):
            stri+='y = {}'.format(y)
            if y < len(nonbeliefstates) - 1:
                stri+=' \\/ '
        for b in beliefcombs:
            beliefset = set()
            for beliefstate in b:
                beliefset = beliefset.union(partitionGrid[beliefstate])
            beliefset =  beliefset -set(gw.targets[0])
            stri1 = ' \\/ (y = {} /\\ ('.format(len(nonbeliefstates)+beliefcombs.index(b))
            count = 0
            for n in range(gw.nagents):
                for x in nonbeliefstates:
                    truebelief = beliefset.intersection(invisibilityset[n][x])
                    if len(truebelief) <= belief_liveness:
                        if count > 0:
                            stri1 += ' \\/ '
                        stri1 += ' {} = {} '.format(agentletters[n],nonbeliefstates.index(x))
                        count+=1
            stri1+='))'
            if count > 0 and count < len(nonbeliefstates):
                stri+=stri1
            if count == len(nonbeliefstates):
                stri+= ' \\/ y = {}'.format(len(nonbeliefstates)+beliefcombs.index(b))
                
        stri += '\n'
        file.write(stri)
   
    
    # Writing env_liveness
    file.write('\n[ENV_LIVENESS]\n')
    stri = 'y = {}'.format(gw.targets[0][0])
    file.write(stri)
    file.close()    

def write_to_slugs_fullobs(infile,gw,inittarg,vel=1):
    states = list(set(gw.states) - set(gw.edges))
 
    filename = infile+'.structuredslugs'
    file = open(filename,'w')
    file.write('[INPUT]\n')
    file.write('y:0...{}\n'.format(len(states) - 1))
    file.write('[OUTPUT]\n')
    agentletters = ['x','z','a','b','c']
    for n in range(gw.nagents):
        file.write(agentletters[n]+':0...{}\n'.format(len(states)-1))

    file.write('[ENV_INIT]\n')
    file.write('y = {}\n'.format(states.index(inittarg)))
    file.write('[SYS_INIT]\n')
    for n in range(gw.nagents):
        file.write(agentletters[n]+' = {}\n'.format(states.index(gw.current[n])))

    # writing env_trans
    file.write('\n[ENV_TRANS]\n')
    for y in range(len(states)):
        for x in range(len(states)):
            sagent = states[x]
            stri = " (x = {} /\\ y = {}) -> ".format(x,y)
            senv = states[y]
            beliefset = set()
            for a in range(gw.nactions):
                for t in np.nonzero(gw.prob[gw.actlist[a]][senv])[0]:
                    stri += ' y\' = {} \\/'.format(states.index(t))
            stri = stri[:-3]
            stri += '\n'
            file.write(stri)
            for n in range(gw.nagents):
                file.write("{} = {} -> !y' = {}\n".format(agentletters[n],x,states.index(sagent)))


    # Writing env_safety
    for obs in gw.obstacles:
        file.write('!y = {}\n'.format(states.index(obs)))

    for n in range(gw.nagents):
        # file.write('!y = {}\n'.format(agentletters[n]))
        file.write('!y = {}\n'.format(states.index(gw.targets[n][0])))

    # writing sys_trans
    file.write('\n[SYS_TRANS]\n')
    for n in range(gw.nagents):
        for x in range(len(states)):
            s = states[x]
            stri = "{} = {} -> ".format(agentletters[n], x)
            t = reach_states(gw,{s})
            for i in range(1,vel):
                t.update(reach_states(gw,t))
            for t2 in t:
                stri += ' {}\' = {} \\/ '.format(agentletters[n], states.index(t2))
            stri = stri[:-3]
            stri += '\n'
            file.write(stri)
    # Writing sys_safety
        for obs in gw.obstacles:
            file.write('!{} = {}\n'.format(agentletters[n],states.index(obs)))

    for s in set(states):
        for n in range(gw.nagents):
            stri = 'y = {} -> !{} = {}\n'.format(states.index(s),agentletters[n],states.index(s))
            file.write(stri)
            stri = 'y = {} -> !{}\' = {}\n'.format(states.index(s),agentletters[n],states.index(s))
            file.write(stri)

    if gw.nagents > 1:
        for s in states:
            for n in range(gw.nagents):
                stri = '{} = {} ->'.format(agentletters[n],states.index(s))
                for m in range(gw.nagents):
                    if m!= n:
                        stri += ' !{} = {} /\\'.format(agentletters[m],states.index(s))
                stri = stri[:-2]
                stri += '\n'
                file.write(stri)

    # Writing sys_liveness
    file.write('\n[SYS_LIVENESS]\n')
    for n in range(gw.nagents):
        file.write('{} = {}\n'.format(agentletters[n],states.index(gw.targets[n][0])))

    # Writing env_liveness
    file.write('\n[ENV_LIVENESS]\n')
    file.close()    


def write_to_slugs_belief_multipletargets(infile,gw,vel=1,belief_partitions=0,beliefconstraint = 1):
    agentletters = ['x','z','a','b','c']
    targetletters = ['y','d','e','f','g']
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
    for n in range(len(gw.moveobstacles)):
        file.write(targetletters[n]+':0...{}\n'.format(len(allstates) - 1))

    file.write('[OUTPUT]\n')
    for n in range(gw.nagents):
        file.write(agentletters[n]+':0...{}\n'.format(len(nonbeliefstates)-1))

    file.write('[ENV_INIT]\n')
    for n in range(len(gw.moveobstacles)):
        file.write(targetletters[n]+' = {}\n'.format(nonbeliefstates.index(gw.moveobstacles[n])))
    file.write('[SYS_INIT]\n')
    for n in range(gw.nagents):
        file.write(agentletters[n]+' = {}\n'.format(nonbeliefstates.index(gw.current[n])))

    # writing env_trans
    file.write('\n[ENV_TRANS]\n')
    for targn in range(len(gw.moveobstacles)):
        for y in range(len(allstates)):
            if allstates[y] in nonbeliefstates:
                for x in range(len(nonbeliefstates)):
                    sagent = nonbeliefstates[x]
                    stri = " (x = {} /\\ {} = {}) -> ".format(x,targetletters[targn],y)
                    senv = allstates[y]
                    beliefset = set()
                    for a in range(gw.nactions):
                        for t in np.nonzero(gw.prob[gw.actlist[a]][senv])[0]:
                            if not any(t in invisibilityset[n][sagent] for n in range(gw.nagents)):
                                stri += ' {}\' = {} \\/'.format(targetletters[targn],allstates.index(t))
                            else:
                                t2 = partitionGrid.keys()[[inv for inv in range(len(partitionGrid.values())) if t in partitionGrid.values()[inv]][0]]
                                beliefset.add(t2)
                    if len(beliefset) > 0:
                        b2 = allstates[len(nonbeliefstates) + beliefcombs.index(beliefset)]
                        stri += ' {}\' = {} \\/'.format(targetletters[targn],allstates.index(b2))
                    stri = stri[:-3]
                    stri += '\n'
                    file.write(stri)
                    for n in range(gw.nagents):
                        file.write("{} = {} -> !{}' = {}\n".format(agentletters[n],x,targetletters[targn],allstates.index(sagent)))

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
                        stri = " (x = {} /\\ {} = {}) -> ".format(x,targetletters[targn],y)
                        beliefset = set()
                        beliefset = beliefset.union(beliefcombstate)
                        for b in beliefstates:
                            for a in range(gw.nactions):
                                for t in np.nonzero(gw.prob[gw.actlist[a]][b])[0]:
                                    if not any(t in invisibilityset[n][sagent] for n in range(gw.nagents)):
                                        stri += ' {}\' = {} \\/'.format(targetletters[targn],allstates.index(t))
                                    else:
                                        t2 = partitionGrid.keys()[[inv for inv in range(len(partitionGrid.values())) if t in partitionGrid.values()[inv]][0]]
                                        beliefset.add(t2)
                            if len(beliefset) > 0:
                                b2 = allstates[len(nonbeliefstates) + beliefcombs.index(beliefset)]
                                stri += ' {}\' = {} \\/'.format(targetletters[targn],allstates.index(b2))
                        stri = stri[:-3]
                        stri += '\n'
                        file.write(stri)


    # Writing env_safety
    for obs in gw.obstacles:
        for targn in range(len(gw.moveobstacles)):
            file.write('!{} = {}\n'.format(targetletters[targn],allstates.index(obs)))

    for n in range(gw.nagents):
        for targn in range(len(gw.moveobstacles)):
        # file.write('!y = {}\n'.format(agentletters[n]))
            file.write('!{} = {}\n'.format(targetletters[targn],allstates.index(gw.targets[n][0])))

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
        for targn in range(len(gw.moveobstacles)):
            for n in range(gw.nagents):
                stri = '{} = {} -> !{} = {}\n'.format(targetletters[targn],allstates.index(s),agentletters[n],nonbeliefstates.index(s))
                file.write(stri)
                stri = '{} = {} -> !{}\' = {}\n'.format(targetletters[targn],allstates.index(s),agentletters[n],nonbeliefstates.index(s))
                file.write(stri)


    combined_belief = list(itertools.product(beliefcombs,repeat=len(gw.moveobstacles)))
    for b in combined_belief:
        beliefset = set()
        for targb in b:
            for beliefstate in targb:
                beliefset = beliefset.union(partitionGrid[beliefstate])
        if len(beliefset) > beliefconstraint:
            for targn in range(len(gw.moveobstacles)):
                stri = '{} = {} /\\ '.format(targetletters[targn],len(nonbeliefstates)+beliefcombs.index(b[targn]))
            stri = stri[:-3]
            counter = 0 #To check if the visible states from target location brings the beliefset below the constraint
            stri += '-> ('
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
    for targn in range(len(gw.moveobstacles)):
        file.write('{} = {}\n'.format(targetletters[targn], nonbeliefstates.index(gw.ncols+2)))
    file.close()
