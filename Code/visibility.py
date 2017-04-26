__author__ = 'sudab'

import numpy as np
import shapely.geometry


def invis(gw, state):
    targcoords = list(gw.coords(state))
    targcoords[0] += 0.5
    targcoords[1] += 0.5
    invisstates = set()
    for s in gw.states:
        statecoords = list(gw.coords(s))
        statecoords[0] += 0.5
        statecoords[1] += 0.5
        line = shapely.geometry.LineString([targcoords, statecoords])
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
