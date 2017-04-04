__author__ = 'sudab'

import numpy as np
import shapely.geometry


def invis(gw, state):
    targcoords = gw.coords(state)
    invisstates = set()
    for s in gw.states:
        statecoords = gw.coords(s)
        line = shapely.geometry.LineString([list(targcoords), list(statecoords)])
        for obs in gw.obstacles:
            obscoordsupleft = list(gw.coords(obs))
            obscoordsupright = [obscoordsupleft[0] + 0.99, obscoordsupleft[1]]
            obscoordsbotleft = [obscoordsupleft[0], obscoordsupleft[1] + 0.99]
            obscoordsbotright = [obscoordsupleft[0] + 0.99, obscoordsupleft[1] + 0.99]
            obshape = shapely.geometry.Polygon([obscoordsupleft, obscoordsupright, obscoordsbotright, obscoordsbotleft])
            isVis = not line.intersects(obshape)
            if not isVis:
                invisstates.add(s)
                break
    invisstates = invisstates - set(gw.walls)
    return frozenset(invisstates)


def isVis(gw, state, target):
    invisstates = invis(gw, state)
    visstates = set(gw.states) - invisstates - set(gw.walls)
    if target in visstates:
        return True
    else:
        return False
