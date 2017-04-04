__author__ = 'sudab'

import numpy as np
import visibility

def write_to_slugs(gw,inittarg):
    agentstates = list(set(gw.states)- set(gw.edges))
    agenttrans = set()
    for s in set(gw.states) - set(gw.walls):
        for a in range(gw.nactions):
            for t in np.nonzero(gw.prob[gw.actlist[a]][s])[0]:
                agenttrans.add((agentstates.index(s),a,agentstates.index(t)))
    xstates = list(set(gw.states) - set(gw.edges))

    invisibilityset = dict.fromkeys(set(gw.states) - set(gw.edges),frozenset({gw.nrows*gw.ncols+1}))
    for s in set(gw.states) - set(gw.edges):
        invisibilityset[s] = visibility.invis(gw,s) - set(gw.targets)
        if s in gw.obstacles:
            invisibilityset[s] = -1
    invisstates = list(set(invisibilityset.values()))
    for s in invisibilityset.values():
        if s not in invisstates:
            invisstates.append(s)
    envtransitions = set()
    for s in set(gw.states) - set(gw.edges):
        for a in range(gw.nactions):
            for t in np.nonzero(gw.prob[gw.actlist[a]][s])[0]:
                envtransitions.add(frozenset({(invisstates.index(invisibilityset[s]),invisstates.index(invisibilityset[t]))}))
    print envtransitions
    filename = 'slugs_input.salt'
    file = open(filename,'w')
    file.write('controller Visgame where\n\n')
    file.write('-- Inputs ----------------------------------------------------------\n\n')
    file.write('input y : Int 0 ... {} = {}\n\n'.format(len(xstates),invisstates.index(invisibilityset[inittarg])))
    file.write('-- Outputs ----------------------------------------------------------\n\n')
    file.write('output x : Int 0 ... {} = {}\n\n'.format(len(xstates),xstates.index(gw.current)))

    # writing env_trans
    file.write('env_trans\n')
    for x in range(len(xstates)):
        s = xstates[x]
        str = "  y == {} -> ".format(x)
        counter = 1
        for a in range(gw.nactions):
            for t in np.nonzero(gw.prob[gw.actlist[a]][s])[0]:
                if counter == 1:
                    str += ' y\' == {}'.format(xstates.index(t))
                    counter += 1
                else:
                    str += ' \\/ y\' == {} '.format(xstates.index(t))
                    counter += 1
        if counter > 1:
            str += '\n'
            file.write(str)
    # Writing env_safety
    for obs in gw.obstacles:
        file.write('  y != {}\n'.format(xstates.index(obs)))
    file.write('  y != {}\n'.format(xstates.index(gw.targets[0])))

    # writing sys_trans
    file.write('\nsys_trans\n')
    for x in range(len(xstates)):
        s = xstates[x]
        str = "  x == {} -> ".format(x)
        counter = 1
        for a in range(gw.nactions):
            for t in np.nonzero(gw.prob[gw.actlist[a]][s])[0]:
                if counter == 1:
                    str += ' x\' == {}'.format(xstates.index(t))
                    counter += 1
                else:
                    str += ' \\/ x\' == {} '.format(xstates.index(t))
                    counter += 1
        if counter > 1:
            str += '\n'
            file.write(str)
    # Writing sys_safety
    for obs in gw.obstacles:
        file.write('  x != {}\n'.format(xstates.index(obs)))

    for s in xstates:
        if s not in gw.obstacles:
            invisstates = invisibilityset[s]
            if len(invisstates) > 1:
                str = '  y == {} -> x != {} '.format(xstates.index(s),xstates.index(s))
                for x in invisstates:
                    str += ' /\\ x != {}'.format(xstates.index(x))
                str += '\n'
                file.write(str)

    # Writing sys_liveness
    file.write('\nsys_liveness\n')
    file.write('  x == {}\n'.format(xstates.index(gw.targets[0])))

    # Writing env_liveness
    file.write('\nenv_liveness\n')
    # file.write('y = {}\n'.format(xstates.index(gw.current)))
    # file.write('y = {}\n'.format(xstates.index(inittarg)))
    # file.write('y = {}\n'.format(xstates.index(88)))
    file.write('  y == {}\n'.format(xstates.index(22)))
    file.close()

