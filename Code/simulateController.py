__author__ = 'sudab'
import random
import simplejson as json
import time
import copy
import visibility


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