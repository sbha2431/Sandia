__author__ = 'sudab'
import copy
import math
def partitionGrid(gw,number_of_partitions):
    n = copy.deepcopy(number_of_partitions)

    if n == 1:
        return [gw.states]
    partition = [None]*n
    partcols = int(math.ceil(math.sqrt(n)))
    partrows = int(math.ceil(n / partcols))
    width = gw.ncols / partcols
    height = gw.nrows/ partrows
    colstates = dict.fromkeys(range(partcols),None)
    rowstates = dict.fromkeys(range(partrows),None)
    partitiondict = {(x,y): set() for x in range(partrows) for y in range(partcols)}
    for k in range(partcols):
        if k == partcols - 1: # if we are the last column
            colstates[k] = range(k*width,gw.ncols)
        else:
            colstates[k] = range(k*width,(k+1)*width)


    for k in range(partrows):
        rowstates[k] = range(k*height,(k+1)*height)
        if k == partrows - 1: # if we are the last column
            rowstates[k] = range(k*height, gw.nrows)

    for s in set(gw.states) - set(gw.walls):
        scoords = gw.coords(s)
        scol = [t for t in range(len(colstates.values())) if scoords[1] in colstates.values()[t]][0]
        srow = [t for t in range(len(rowstates.values())) if scoords[0] in rowstates.values()[t]][0]
        partitiondict[(srow,scol)].add(s)
    return partitiondict
