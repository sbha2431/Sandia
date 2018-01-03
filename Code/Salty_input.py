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


def write_to_slugs_part(infile,gw,init,initmovetarget,targets,vel=1,visdist = 5,groundstations = [],partitionGrid =[], belief_safety = 0, belief_liveness = 0, target_reachability = False):
    nonbeliefstates = gw.states
    beliefcombs = powerset(partitionGrid.keys())

    allstates = copy.deepcopy(nonbeliefstates)
    for i in range(gw.nstates,gw.nstates + len(beliefcombs)):
        allstates.append(i)

    invisibilityset = dict.fromkeys(set(gw.states),frozenset({gw.nrows*gw.ncols+1}))
    for s in set(gw.states):
        if s not in groundstations:
            invisibilityset[s] = visibility.invis(gw,s,visdist)
        else:
            invisibilityset[s] = visibility.invis(gw,s,10000)
        if s in gw.obstacles:
            invisibilityset[s] = {-1}

    filename = infile+'.structuredslugs'
    file = open(filename,'w')
    file.write('[INPUT]\n')
    file.write('st:0...{}\n'.format(len(allstates) -1))

    file.write('[OUTPUT]\n')
    file.write('s:0...{}\n'.format(len(gw.states)-1))
    # for v in range(vel):
    #     file.write('u{}:0...{}\n'.format(v,gw.nactions-1))

    file.write('[ENV_INIT]\n')
    file.write('st = {}\n'.format(initmovetarget))

    file.write('[SYS_INIT]\n')
    file.write('s = {}\n'.format(init))

    # writing env_trans
    file.write('\n[ENV_TRANS]\n')
    for st in allstates:
        if st in nonbeliefstates:
            for s in nonbeliefstates:
                stri = "(s = {} /\\ st = {}) -> ".format(s,st)
                beliefset = set()
                for a in range(gw.nactions):
                    for t in np.nonzero(gw.prob[gw.actlist[a]][st])[0]:
                        if not t in invisibilityset[s]:
                            stri += 'st\' = {} \\/'.format(t)
                        else:
                            if not t == s and t not in targets: # not allowed to move on agent's position
                                try:
                                    partgridkeyind = [inv for inv in range(len(partitionGrid.values())) if t in partitionGrid.values()[inv]][0]
                                except:
                                    print t,st,s
                                t2 = partitionGrid.keys()[partgridkeyind]
                                beliefset.add(t2)
                if len(beliefset) > 0:
                    b2 = allstates[len(nonbeliefstates) + beliefcombs.index(beliefset)]
                    stri += ' st\' = {} \\/'.format(b2)
                stri = stri[:-3]
                stri += '\n'
                file.write(stri)
                file.write("s = {} -> !st' = {}\n".format(s,s))
                # file.write("s = {} -> !st = {}\n".format(s,s))

        else:
            for s in nonbeliefstates:
                invisstates = invisibilityset[s]
                visstates = set(nonbeliefstates) - invisstates

                beliefcombstate = beliefcombs[st - len(nonbeliefstates)]
                beliefstates = set()
                for currbeliefstate in beliefcombstate:
                    beliefstates = beliefstates.union(partitionGrid[currbeliefstate])
                beliefstates = beliefstates - set(targets) # remove taret positions (no transitions from target positions)
                beliefstates_vis = beliefstates.intersection(visstates)
                beliefstates_invis = beliefstates - beliefstates_vis

                if belief_safety > 0 and len(beliefstates_invis) > belief_safety:
                    continue # no transitions from error states

                if len(beliefstates) > 0:
                    stri = "(s = {} /\\ st = {}) -> ".format(s,st)

                    beliefset = set()
                    for b in beliefstates:
                        for a in range(gw.nactions):
                            for t in np.nonzero(gw.prob[gw.actlist[a]][b])[0]:
                                if not t in invisibilityset[s]:
                                    stri += ' st\' = {} \\/'.format(t)
                                else:
                                    if t in gw.targets[0]:
                                        continue
                                    t2 = partitionGrid.keys()[[inv for inv in range(len(partitionGrid.values())) if t in partitionGrid.values()[inv]][0]]
                                    beliefset.add(t2)
                    if len(beliefset) > 0:
                        b2 = allstates[len(nonbeliefstates) + beliefcombs.index(beliefset)]
                        stri += ' st\' = {} \\/'.format(b2)


                    stri = stri[:-3]
                    stri += '\n'
                    file.write(stri)

    # Writing env_safety
    for obs in gw.obstacles:
        file.write('!st = {}\n'.format(obs))

    if target_reachability:
        for t in targets:
            file.write('!st = {}\n'.format(t))

    # writing sys_trans
    file.write('\n[SYS_TRANS]\n')
    for s in nonbeliefstates:
        uset = list(itertools.product(range(len(gw.actlist)),repeat=vel))
        stri = "s = {} -> ".format(s)
        for u in uset:
            # for v in range(vel):
            #     stri += "u{} = {} /\\ ".format(v,u[v])
            # stri = stri[:-3]
            # stri += ' -> '
            snext = copy.deepcopy(s)
            for v in range(vel):
                act = gw.actlist[u[v]]
                snext = np.nonzero(gw.prob[act][snext])[0][0]
            stri += '(s\' = {}) \\/'.format(snext)
        stri = stri[:-3]
        stri += '\n'
        file.write(stri)
# Writing sys_safety
    for obs in gw.obstacles:
        file.write('!s = {}\n'.format(obs))


    for s in set(nonbeliefstates):
        stri = 'st = {} -> !s = {}\n'.format(s,s)
        file.write(stri)
        stri = 'st = {} -> !s\' = {}\n'.format(s,s)
        file.write(stri)

    if belief_safety > 0:
        for b in beliefcombs:
            beliefset = set()
            for beliefstate in b:
                beliefset = beliefset.union(partitionGrid[beliefstate])
            beliefset =  beliefset -set(gw.targets[0])
            if len(beliefset) > belief_safety:
                stri = 'st = {} -> '.format(len(nonbeliefstates)+beliefcombs.index(b))
                counter = 0
                stri += '('
                for x in nonbeliefstates:
                    invisstates = invisibilityset[x]
                    beliefset_invis = beliefset.intersection(invisstates)
                    if len(beliefset_invis) > belief_safety:
                        stri += '!s = {} /\\ '.format(nonbeliefstates.index(x))
                        counter += 1
                stri = stri[:-3]
                stri += ')\n'
                if counter > 0:
                    file.write(stri)



    # Writing sys_liveness
    file.write('\n[SYS_LIVENESS]\n')
    if target_reachability:
        for t in targets:
            file.write('s = {}\n'.format(nonbeliefstates.index(t)))

    stri  = ''
    if belief_liveness >0:
        for y in range(len(nonbeliefstates)):
            stri+='st = {}'.format(y)
            if y < len(nonbeliefstates) - 1:
                stri+=' \\/ '
        for b in beliefcombs:
            beliefset = set()
            for beliefstate in b:
                beliefset = beliefset.union(partitionGrid[beliefstate])
            beliefset =  beliefset -set(gw.targets[0])
            stri1 = ' \\/ (st = {} /\\ ('.format(len(nonbeliefstates)+beliefcombs.index(b))
            count = 0
            for x in nonbeliefstates:
                truebelief = beliefset.intersection(invisibilityset[x])
                if len(truebelief) <= belief_liveness:
                    if count > 0:
                        stri1 += ' \\/ '
                    stri1 += ' s = {} '.format(nonbeliefstates.index(x))
                    count+=1
            stri1+='))'
            if count > 0 and count < len(nonbeliefstates):
                stri+=stri1
            if count == len(nonbeliefstates):
                stri+= ' \\/ st = {}'.format(len(nonbeliefstates)+beliefcombs.index(b))

        stri += '\n'
        file.write(stri)
    return invisibilityset

def write_to_slugs_part_dist(infile,gw,init,initmovetarget,targets,vel=1,visdist = 5,allowed_states = [],fullvis_states = [],partitionGrid =dict(), belief_safety = 0, belief_liveness = 0, target_reachability = False):
    nonbeliefstates = gw.states
    beliefcombs = powerset(partitionGrid.keys())

    allstates = copy.deepcopy(nonbeliefstates)
    for i in range(gw.nstates,gw.nstates + len(beliefcombs)):
        allstates.append(i)
    allstates.append(len(allstates)) # nominal state if target leaves allowed region

    invisibilityset = dict.fromkeys(set(gw.states),frozenset({gw.nrows*gw.ncols+1}))
    for s in set(nonbeliefstates):
        invisibilityset[s] = visibility.invis(gw,s,visdist).intersection(set(allowed_states))
        invisibilityset[s] = invisibilityset[s] - set(fullvis_states)
        if s in gw.obstacles:
            invisibilityset[s] = {-1}

    filename = infile+'.structuredslugs'
    file = open(filename,'w')
    file.write('[INPUT]\n')
    file.write('st:0...{}\n'.format(len(allstates) -1))


    file.write('[OUTPUT]\n')
    file.write('sane:0...1\n')
    file.write('s:0...{}\n'.format(len(gw.states)-1))

    # for v in range(vel):
    #     file.write('u{}:0...{}\n'.format(v,gw.nactions-1))

    file.write('[ENV_INIT]\n')

    if initmovetarget in allowed_states:
        file.write('st = {}\n'.format(initmovetarget))
    else:
        file.write('st = {}\n'.format(allstates[-1]))

    file.write('[SYS_INIT]\n')
    file.write('sane=0\n')
    file.write('s = {}\n'.format(init))


    # writing env_trans
    file.write('\n[ENV_TRANS]\n')
    for st in set(allstates) - (set(nonbeliefstates) - set(allowed_states)): #Only allowed states and belief states
        if st in allowed_states:
            for s in allowed_states:
                stri = "(s = {} /\\ st = {}) -> ".format(s,st)
                beliefset = set()
                for a in range(gw.nactions):
                    for t in np.nonzero(gw.prob[gw.actlist[a]][st])[0]:
                        if t in allowed_states:
                            if not t in invisibilityset[s]:
                                stri += 'st\' = {} \\/'.format(t)
                            else:
                                if not t == s and t not in targets: # not allowed to move on agent's position
                                    try:
                                        partgridkeyind = [inv for inv in range(len(partitionGrid.values())) if t in partitionGrid.values()[inv]][0]
                                        t2 = partitionGrid.keys()[partgridkeyind]
                                        beliefset.add(t2)
                                    except:
                                        print t
                        elif t not in allowed_states and t not in gw.obstacles:
                            stri += 'st\' = {} \\/'.format(allstates[-1])
                if len(beliefset) > 0:
                    b2 = allstates[len(nonbeliefstates) + beliefcombs.index(beliefset)]
                    stri += ' st\' = {} \\/'.format(b2)
                stri = stri[:-3]
                stri += '\n'
                file.write(stri)
                file.write("s = {} -> !st' = {}\n".format(s,s))
                # file.write("s = {} -> !st = {}\n".format(s,s))
        elif st == allstates[-1]:
            stri = "st = {} -> ".format(st)
            for t in fullvis_states:
                stri += "st' = {} \\/ ".format(t)
            stri += "st' = {}".format(st)
            stri += '\n'
            file.write(stri)
        else:
            for s in allowed_states:
                invisstates = invisibilityset[s]
                visstates = set(nonbeliefstates) - invisstates

                beliefcombstate = beliefcombs[st - len(nonbeliefstates)]
                beliefstates = set()
                for currbeliefstate in beliefcombstate:
                    beliefstates = beliefstates.union(partitionGrid[currbeliefstate])
                beliefstates = beliefstates - set(targets) # remove taret positions (no transitions from target positions)
                beliefstates_vis = beliefstates.intersection(visstates)
                beliefstates_invis = beliefstates - beliefstates_vis

                if belief_safety > 0 and len(beliefstates_invis) > belief_safety:
                    continue # no transitions from error states

                if len(beliefstates) > 0:
                    stri = "(s = {} /\\ st = {}) -> ".format(s,st)

                    beliefset = set()
                    for b in beliefstates:
                        for a in range(gw.nactions):
                            for t in np.nonzero(gw.prob[gw.actlist[a]][b])[0]:
                                if not t in invisibilityset[s]:
                                    if t in allowed_states:
                                        stri += ' st\' = {} \\/'.format(t)
                                else:
                                    if t in gw.targets[0]:
                                        continue
                                    t2 = partitionGrid.keys()[[inv for inv in range(len(partitionGrid.values())) if t in partitionGrid.values()[inv]][0]]
                                    beliefset.add(t2)
                    if len(beliefset) > 0:
                        b2 = allstates[len(nonbeliefstates) + beliefcombs.index(beliefset)]
                        stri += ' st\' = {} \\/'.format(b2)


                    stri = stri[:-3]
                    stri += '\n'
                    file.write(stri)

    # Writing env_safety
    for obs in gw.obstacles:
        if obs in allowed_states:
            file.write('!st = {}\n'.format(obs))

    if target_reachability:
        for t in targets:
            file.write('!st = {}\n'.format(t))

    # writing sys_trans
    file.write('\n[SYS_TRANS]\n')
    file.write("s = s' <-> sane= 0\n")
    file.write("!s = s' <-> sane= 1\n")
    for s in nonbeliefstates:
        if s in allowed_states:
            uset = list(itertools.product(range(len(gw.actlist)),repeat=vel))
            stri = "s = {} -> ".format(s)
            for u in uset:
                # for v in range(vel):
                #     stri += "u{} = {} /\\ ".format(v,u[v])
                # stri = stri[:-3]
                # stri += ' -> '
                snext = copy.deepcopy(s)
                for v in range(vel):
                    act = gw.actlist[u[v]]
                    snext = np.nonzero(gw.prob[act][snext])[0][0]
                stri += '(s\' = {}) \\/'.format(snext)
            stri = stri[:-3]
            stri += '\n'
            file.write(stri)
        else:
            file.write("!s = {}\n".format(s))
# Writing sys_safety
    for obs in gw.obstacles:
        if obs in allowed_states:
            file.write('!s = {}\n'.format(obs))


    for s in set(allowed_states):
        stri = 'st = {} -> !s = {}\n'.format(s,s)
        file.write(stri)
        stri = 'st = {} -> !s\' = {}\n'.format(s,s)
        file.write(stri)

    if belief_safety > 0:
        for b in beliefcombs:
            beliefset = set()
            for beliefstate in b:
                beliefset = beliefset.union(partitionGrid[beliefstate])
            beliefset =  beliefset -set(gw.targets[0])
            if len(beliefset) > belief_safety:
                stri = 'st = {} -> '.format(len(nonbeliefstates)+beliefcombs.index(b))
                counter = 0
                stri += '('
                for x in allowed_states:
                    invisstates = invisibilityset[x]
                    beliefset_invis = beliefset.intersection(invisstates)
                    if len(beliefset_invis) > belief_safety:
                        stri += '!s = {} /\\ '.format(nonbeliefstates.index(x))
                        counter += 1
                stri = stri[:-3]
                stri += ')\n'
                if counter > 0:
                    file.write(stri)



    # Writing sys_liveness
    file.write('\n[SYS_LIVENESS]\n')
    if target_reachability:
        for t in targets:
            file.write('s = {}\n'.format(nonbeliefstates.index(t)))

    stri  = ''
    if belief_liveness >0:
        for st in allowed_states:
            stri+='st = {}'.format(st)
            if st != allowed_states[-1]:
                stri+=' \\/ '
        for b in beliefcombs:
            beliefset = set()
            for beliefstate in b:
                beliefset = beliefset.union(partitionGrid[beliefstate])
            beliefset =  beliefset -set(gw.targets[0])
            stri1 = ' \\/ (st = {} /\\ ('.format(len(nonbeliefstates)+beliefcombs.index(b))
            count = 0
            for x in allowed_states:
                truebelief = beliefset.intersection(invisibilityset[x])
                if len(truebelief) <= belief_liveness:
                    if count > 0:
                        stri1 += ' \\/ '
                    stri1 += ' s = {} '.format(nonbeliefstates.index(x))
                    count+=1
            stri1+='))'
            if count > 0 and count < len(allowed_states):
                stri+=stri1
            if count == len(allowed_states):
                stri+= ' \\/ st = {}'.format(len(nonbeliefstates)+beliefcombs.index(b))
        stri += ' \\/ st = {}'.format(allstates[-1])
        for st in set(nonbeliefstates)- set(allowed_states):
            stri += ' \\/ st = {}'.format(st)
        stri += '\n'
        file.write(stri)

    file.write('\n[ENV_LIVENESS]\n')
    # for t in targets:
    #     file.write('st = {}\n'.format(t+1))

    return invisibilityset

