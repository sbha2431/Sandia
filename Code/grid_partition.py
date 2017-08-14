__author__ = 'sudab'
import copy
import math
def partitionGrid(gw,number_of_partitions):
    n = copy.deepcopy(number_of_partitions)

    if n == 1:
        return [gw.states]
    partition = [None]*n
    partcols = int(math.ceil(math.sqrt(n)))
    partrows = int(math.ceil(float(n) / partcols))
    width = int(math.ceil(float(gw.ncols-2) / partcols)) #-2 accounts for walls
    height = int(math.ceil(float(gw.nrows-2)/ partrows))
    colstates = dict.fromkeys(range(partcols),None)
    rowstates = dict.fromkeys(range(partrows),None)
    partitiondict = {(x,y,0): set() for x in range(partrows) for y in range(partcols)}
    for k in range(partcols):
        if k == partcols - 1: # if we are the last column
            colstates[k] = range(k*width,gw.ncols-1)
        else:
            colstates[k] = range(k*width,(k+1)*width)

    for k in colstates.keys():
        if len(colstates[k]) == 0:
            colstates.__delitem__(k)

    for k in range(partrows):
        rowstates[k] = range(k*height,(k+1)*height)
        if k == partrows - 1: # if we are the last column
            rowstates[k] = range(k*height, gw.nrows-1)

    for s in set(gw.states) - set(gw.walls):
        scoords = gw.coords(s)
        scol = [t for t in range(len(colstates.values())) if scoords[1] in colstates.values()[t]][0]
        srow = [t for t in range(len(rowstates.values())) if scoords[0] in rowstates.values()[t]][0]
        partitiondict[(srow,scol,0)].add(s)
    return partitiondict

def partitionState(gw,partitiondict,partkey,refine):

    partitiondict_refine = copy.deepcopy(partitiondict)
    partitiondict_refine[partkey] = set()
    partitiondict_refine[(partkey[0],partkey[1],partkey[2]+1)] = set()
    rownum = 1
    colnum = 0
    for ind in range(len(partitiondict[partkey])-1):
        if ind == 0:
            startcol = sorted(partitiondict[partkey])[ind]
        s = sorted(partitiondict[partkey])[ind]
        next_s = sorted(partitiondict[partkey])[ind+1]
        if len(set(range(s,next_s)).intersection(gw.edges))>0:
            rownum += 1
            colnum = max([colnum,s - startcol])
            startcol = next_s
        # elif len(set(range(s,next_s)).intersection(gw.edges))==0:
        #     colnum = max([colnum,s - startcol])
    colnum+=1
    rowval = 1
    if refine == 'col':
        for ind in range(len(partitiondict[partkey])-1):
            if ind == 0:
                startcol = sorted(partitiondict[partkey])[ind]
            s = sorted(partitiondict[partkey])[ind]
            next_s = sorted(partitiondict[partkey])[ind+1]
            if len(set(range(s,next_s)).intersection(gw.edges))>0:
                partitiondict_refine[(partkey[0],partkey[1],partkey[2]+1)].add(s)
                partitiondict_refine[partkey].add(next_s)
                startcol = next_s
            else:
                colval = s - startcol + 1
                if colval <= float(colnum)/2:
                    partitiondict_refine[partkey].add(s)
                else:
                    partitiondict_refine[(partkey[0],partkey[1],partkey[2]+1)].add(s)
            if ind == range(len(partitiondict[partkey])-1)[-1]:
                if next_s not in partitiondict_refine[partkey]:
                    partitiondict_refine[(partkey[0],partkey[1],partkey[2]+1)].add(next_s)

    elif refine == 'row':
        for ind in range(len(partitiondict[partkey])-1):
            s = sorted(partitiondict[partkey])[ind]
            next_s = sorted(partitiondict[partkey])[ind+1]
            if rowval <= float(rownum)/2:
                partitiondict_refine[partkey].add(s)
                if len(set(range(s,next_s)).intersection(gw.edges))>0:
                    rowval += 1
            else:
                partitiondict_refine[(partkey[0],partkey[1],partkey[2]+1)].add(s)
                if len(set(range(s,next_s)).intersection(gw.edges))>0:
                    rowval += 1
            if ind == range(len(partitiondict[partkey])-1)[-1]:
                    if next_s not in partitiondict_refine[partkey]:
                        partitiondict_refine[(partkey[0],partkey[1],partkey[2]+1)].add(next_s)
    return partitiondict_refine

def partitionState_manual(partitiondict,partkey,states):
    partitiondict_refine = copy.deepcopy(partitiondict)
    p1 = partitiondict[partkey].intersection(states)
    p2 = partitiondict[partkey].difference(states)
    if not p1 or not p2:
        return partitiondict_refine
    partitiondict_refine[partkey] = set()
    partitiondict_refine[(partkey[0],partkey[1],len(partitiondict)+1)] = set()
    partitiondict_refine[partkey] = partitiondict_refine[partkey].union(partitiondict[partkey].intersection(states))
    partitiondict_refine[(partkey[0],partkey[1],len(partitiondict)+1)] = partitiondict[partkey].difference(states)
    return partitiondict_refine

def refine_partition(partitiondict,partkey,stateSets):
    partitiondict_refine = copy.deepcopy(partitiondict)
    
    new_sets = list()
    new_sets.append(partitiondict[partkey])
    
    for states in stateSets:
        ns = copy.deepcopy(new_sets)        
        new_sets[:] = []        
        while ns:
            p = ns.pop()
            p1 = p.intersection(states)
            p2 = p.difference(states)
            if p1:
                new_sets.append(p1)
            if p2:                
                new_sets.append(p2)
    p = new_sets.pop(0)
    partitiondict_refine[partkey] = p
    for p in new_sets:
        partitiondict_refine[(partkey[0],partkey[1],len(partitiondict_refine)+1)] = p
   
    return partitiondict_refine

def precise_partition(gw):
    count = 0
    partition = dict()
    for s in set(gw.states) - set(gw.walls):
        partition[(0,0,count)] = set()
        partition[(0,0,count)].add(s)
        count = count + 1
    return partition
